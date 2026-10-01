import gdb, json, os, re

START     = "main"
MAX_STEPS = 4000
NODE_MAX  = 256
CHUNK_MAX = 400
FRAME_MAX = 512                        # most bytes of one stack frame to record
STDOUT    = "prog_stdout.txt"
WATCH_MAX = 4                          # x86-64 CPUs have 4 hardware watchpoints, 8 bytes each

ARR_BYTES = 2048                       # most bytes of one heap array to record
steps, KNOWN, FREED = [], {}, set()   # KNOWN: addr -> ("struct", name) or ("array", element type, element size)
ALLOCED = set()                        # every address malloc/calloc/realloc handed to the program
REQ, HOW, COPIED = {}, {}, {}          # addr -> bytes asked for, which call gave it, bytes realloc carried over
ROOTS = []                             # (value, what it points to) for every pointer variable on this step
FREE_ORDER = []                        # addresses in the order free() got them, newest last
EVENTS = []                            # bugs trace.py saw since the last snapshot: double free, bad free, a signal
LIBCALLS = []                          # library calls since the last snapshot, and what the watchpoints caught
WPS = []                               # the watchpoints armed right now
watch_ok = True                        # False once the CPU refuses a hardware watchpoint
our_file = None
OUR_TYPES = []                         # the struct and union types this program defines: candidates for container_of
USED = []                              # (start, usable bytes) of every used heap chunk on this step

def is_ptr(t):  return t.strip_typedefs().code == gdb.TYPE_CODE_PTR
def scalar(t):  return t.strip_typedefs().code in (gdb.TYPE_CODE_INT, gdb.TYPE_CODE_ENUM,
                                                   gdb.TYPE_CODE_CHAR, gdb.TYPE_CODE_BOOL)
TYPES = {}                             # struct key -> gdb.Type, so an anonymous typedef struct can be found again
def sname(t):
    """the key a struct type is recorded and found by: "struct node", or the typedef name of an anonymous one ("Bag")"""
    s = t.strip_typedefs(); n = str(s)
    if "{...}" in n:                                     # typedef struct { ... } Bag: no struct name of its own
        u = t.unqualified()
        n = str(u) if u.code == gdb.TYPE_CODE_TYPEDEF else next((k for k, v in TYPES.items() if v == s), "%s #%d" % (n, len(TYPES) + 1))
    TYPES[n] = s
    return n
def lookup(name):
    """a struct type back from its key"""
    return TYPES.get(name) or gdb.lookup_type(name)
def struct_of(t):
    """the name of the struct a pointer of type t points to, or None"""
    t = t.strip_typedefs()
    if t.code != gdb.TYPE_CODE_PTR: return None
    tgt = t.target().strip_typedefs()
    return sname(t.target()) if tgt.code == gdb.TYPE_CODE_STRUCT else None
def raw(addr, size):
    """size bytes at addr, as hex, lowest address first"""
    if not addr or size <= 0: return None
    try: return bytes(gdb.selected_inferior().read_memory(addr, size)).hex()
    except gdb.error: return None

# ---- watch the allocator, without stopping ----
class MallocRet(gdb.FinishBreakpoint):
    def __init__(self, frame, func, size, old):
        super().__init__(frame, internal=True)
        self.func, self.size, self.old = func, size, old
    def stop(self):
        try:
            a = int(gdb.parse_and_eval("$rax"))                  # the address it just returned
            FREED.discard(a); ALLOCED.add(a)
            if a:
                COPIED[a] = min(REQ.get(self.old, 0), self.size) if self.old else 0   # before REQ changes: realloc may grow in place
                REQ[a], HOW[a] = self.size, self.func
                if self.old and self.old != a: FREED.add(self.old)   # realloc moved it: the old block is gone
        except Exception: pass
        return False
class Malloc(gdb.Breakpoint):                     # malloc, calloc and realloc all hand out blocks
    def __init__(self, fn="malloc"):
        super().__init__(fn, internal=True); self.fn = fn
    def stop(self):
        try:
            a, b = reg("rdi"), reg("rsi")                        # the size you asked for
            size = {"malloc": a, "calloc": a * b, "realloc": b}[self.fn]
            MallocRet(gdb.newest_frame(), self.fn, size, a if self.fn == "realloc" else 0)
        except Exception: pass
        return False
class Free(gdb.Breakpoint):
    def __init__(self): super().__init__("free", internal=True)
    def stop(self):
        try:
            a = int(gdb.parse_and_eval("$rdi"))
            if a:                                                # free(NULL) does nothing: fine
                if a in FREED: EVENTS.append({"kind": "double free", "addr": a})
                else:
                    try: caller = gdb.newest_frame().older()
                    except gdb.error: caller = None
                    if caller and ours(caller) and a not in ALLOCED: EVENTS.append({"kind": "bad free", "addr": a})   # your code freed something malloc never gave
            FREED.add(a); FREE_ORDER.append(a)
        except Exception: pass
        return False

# ---- real gdb watchpoints: catch what a library call (free, malloc, strcpy ...) writes into your memory ----
def ours(frame):
    try:
        s = frame.find_sal()
        return bool(s.symtab) and s.symtab.filename == our_file
    except gdb.error: return False

class Watch(gdb.Breakpoint):
    """a hardware watchpoint on one 8-byte word: the CPU stops the program the moment something writes it"""
    def __init__(self, addr, call):
        super().__init__("*(long *) %d" % addr, gdb.BP_WATCHPOINT, gdb.WP_WRITE, internal=True)
        self.addr, self.call, self.old = addr, call, raw(addr, 8)
    def stop(self):
        try:
            new, f = raw(self.addr, 8), gdb.newest_frame()
            if new != self.old and not ours(f):                  # only writes made inside the library
                self.call["writes"].append({"addr": self.addr, "size": 8, "old": self.old, "new": new, "in": f.name()})
            self.old = new
        except Exception: pass
        return False

def disarm():
    """delete every watchpoint, even one the CPU refused half-way"""
    del WPS[:]
    for b in gdb.breakpoints():
        try:
            if b.type in (gdb.BP_WATCHPOINT, gdb.BP_HARDWARE_WATCHPOINT): b.delete()
        except (gdb.error, RuntimeError): pass

def reg(r): return int(gdb.parse_and_eval("(unsigned long) $" + r))
def chunk_size(p):
    """the size malloc wrote in the header just above the block at p"""
    b = raw(p - 8, 8)
    return int.from_bytes(bytes.fromhex(b), "little") & ~7 if b else 0

def user_mem(p):
    """[start, end) of your variable or heap block that p points into, or None"""
    if not steps or p < 4096: return None
    s = steps[-1]
    for n in s["heap"]:
        if not n["freed"] and n["addr"] <= p < n["addr"] + n["size"]: return n["addr"], n["addr"] + n["size"]
    for fr in s["frames"]:
        for v in fr["vars"]:
            if v["addr"] and v["addr"] <= p < v["addr"] + v["size"]: return v["addr"], v["addr"] + v["size"]
    return None

def plan(func):
    """which 8-byte words this call is likely to write, most likely first, as (words, guess, partial):
       guess   - we picked which freed block malloc will hand back, and may be wrong
       partial - the call may write more words than the watchpoints can cover"""
    a = [reg(r) for r in ("rdi", "rsi", "rdx", "rcx")]
    if func == "free":                                    # the block's first 2 words, and the next chunk's header
        if not a[0]: return [], False, False
        nxt = a[0] - 16 + chunk_size(a[0])
        return [a[0], a[0] + 8, nxt, nxt + 8], False, False
    if func in ("malloc", "calloc", "realloc"):          # malloc hands back the newest freed block of the right size
        n = {"malloc": a[0], "calloc": a[0] * a[1], "realloc": a[1]}[func]
        want, seen, out = max(32, (n + 8 + 15) & ~15), set(), []
        if func == "realloc" and a[0]: out += [a[0], a[0] + 8]
        for p in reversed(FREE_ORDER):
            if p in FREED and p not in seen and chunk_size(p) == want: seen.add(p); out += [p, p + 8]
        guess = len(seen) > 0
        partial = (func == "calloc" and guess and n > 16) or (func == "realloc" and a[0] and n > 16)   # zeroing or copying n bytes
        return out, guess, partial
    out = []                                              # anything else: the memory its pointer arguments point into
    for p in a:
        m = user_mem(p)
        if m: out += list(range(p - p % 8, m[1], 8))
    return out, False, len(set(out)) > WATCH_MAX

ALLOCS = ("malloc", "calloc", "realloc", "free")

def arm(func, line):
    global watch_ok
    disarm()
    words, guess, partial = plan(func)
    call = {"func": func, "line": line, "arg": reg("rdi"), "watched": [], "writes": [], "guess": guess, "partial": partial}
    for w in words:
        if len(WPS) >= WATCH_MAX or not watch_ok: break
        if w in call["watched"] or not raw(w, 8): continue
        try: WPS.append(Watch(w, call)); call["watched"].append(w)
        except (gdb.error, RuntimeError):                 # the CPU has no room: go on without watchpoints
            watch_ok = False; disarm(); del call["watched"][:]
    if call["watched"]: LIBCALLS.append(call)

class LibCall(gdb.Breakpoint):
    """sits on a `call free@plt` in your code, and arms watchpoints just before the library runs"""
    def __init__(self, pc, func, line):
        super().__init__("*%d" % pc, internal=True)
        self.func, self.line = func, line
    def stop(self):
        try: arm(self.func, self.line)
        except Exception: pass
        return False

def lib_calls():
    """every call from your code into a library, as (address, function, line)"""
    blk = gdb.selected_frame().find_sal().symtab.static_block()
    for ins in gdb.selected_frame().architecture().disassemble(blk.start, blk.end - 1):
        m = re.search(r"\bcall\b.*<([\w.]+)@plt>", ins["asm"])
        if m: yield ins["addr"], re.sub(r"^__isoc99_", "", m.group(1)), gdb.find_pc_line(ins["addr"]).line

def ptr_desc(t):
    """what a pointer of type t leads to: ("struct", name), ("array", element type, element size) for int, char ...,
       ("array", "int *", 8, what each element leads to) for int **, char **, struct X **, or None (void *, function pointers)"""
    try:
        t = t.strip_typedefs()
        if t.code != gdb.TYPE_CODE_PTR: return None
        tgt = t.target().strip_typedefs()
        if tgt.code == gdb.TYPE_CODE_STRUCT: return ("struct", sname(t.target()))
        if scalar(tgt) and tgt.sizeof in (1, 2, 4, 8): return ("array", str(tgt.unqualified()), tgt.sizeof)
        if tgt.code == gdb.TYPE_CODE_PTR: return ("array", str(t.target().strip_typedefs().unqualified()), 8, ptr_desc(tgt))   # a pointer array
    except gdb.error: pass
    return None

def words(addr, n):
    """the n 8-byte pointers stored at addr"""
    b = raw(addr, n * 8)
    return [int.from_bytes(bytes.fromhex(b[k * 16:k * 16 + 16]), "little") for k in range(n)] if b else []

def read_array(addr, elem, esize):
    """a malloc'd block of ints or chars: the bytes you asked for, and the ones past its end up to the next chunk's header"""
    csz = chunk_size(addr)
    req = REQ.get(addr, max(0, csz - 8))                     # not seen being allocated: all of its usable bytes
    out = {"addr": addr, "type": "%s [%d]" % (elem, req // esize), "kind": "array", "elem": elem, "esize": esize, "fields": [], "freed": False,
           "size": req, "bytes": raw(addr, min(req, ARR_BYTES)), "header": raw(addr - 16, 16), "how": HOW.get(addr, "malloc")}
    if COPIED.get(addr): out["copied"] = COPIED[addr]
    if req <= ARR_BYTES and csz > req: out["slack"] = raw(addr + req, csz - req)   # up to and including the next header
    return out

NEST_MAX = 3                           # levels of structs inside structs to record
def is_rec(t): return t.strip_typedefs().code in (gdb.TYPE_CODE_STRUCT, gdb.TYPE_CODE_UNION)

def fields_of(v, t, depth=1):
    """the fields of struct (or union) value v: name, type, kind, value, offset (from the start of v), size, target.
       A field that is a struct or union itself also gets its own "fields", NEST_MAX levels deep"""
    fields = []
    for f in t.strip_typedefs().fields():
        if f.name is None: continue
        fv = v[f.name]; ft = fv.type.strip_typedefs()
        if ft.code == gdb.TYPE_CODE_PTR:   kind, val = "ptr", int(fv)
        elif scalar(ft):                   kind, val = "int", int(fv)
        else:                              kind, val = "other", None
        fd = {"name": f.name, "type": str(f.type), "kind": kind, "value": val,
              "offset": f.bitpos // 8, "size": f.type.sizeof,
              "target": str(ft.target()) if kind == "ptr" else None}
        if is_rec(ft) and depth < NEST_MAX: fd["fields"] = fields_of(fv, ft, depth + 1)   # struct point pos: x and y
        fields.append(fd)
    return fields

def ptr_values(v, t, depth=1):
    """every pointer inside struct value v, nested structs too, in field order: (value, what it leads to)"""
    for f in t.strip_typedefs().fields():
        if f.name is None: continue
        fv = v[f.name]; ft = fv.type.strip_typedefs()
        if ft.code == gdb.TYPE_CODE_PTR: yield int(fv), ptr_desc(ft)
        elif is_rec(ft) and depth < NEST_MAX:
            for x in ptr_values(fv, ft, depth + 1): yield x

def read_block(addr, stname):
    t = lookup(stname)
    v = gdb.Value(addr).cast(t.pointer()).dereference()
    fields = fields_of(v, t)
    return {"addr": addr, "type": stname, "fields": fields, "freed": False,
            "size": t.sizeof, "bytes": raw(addr, t.sizeof),
            "header": raw(addr - 16, 16)}          # malloc's chunk header

def frame_mem(frame, vars_):
    """the frame's own bytes, up to just past the return address (x86-64, -O0). A function that calls
       nothing may keep its locals below rsp (the red zone), so start at the lowest variable if that's lower."""
    try:
        rbp = int(frame.read_register("rbp")); rsp = int(frame.read_register("rsp"))
        if not (0 < rsp <= rbp): return {}
        lo = min([rsp] + [v["addr"] for v in vars_ if v.get("addr") and v["addr"] < rbp])
        lo -= lo % 8
        if rbp + 16 - lo > FRAME_MAX: return {}
        return {"rbp": rbp, "rsp": rsp, "lo": lo, "frame_bytes": raw(lo, rbp + 16 - lo)}
    except (gdb.error, ValueError): return {}

def var_entry(out, sym, v):
    """one variable's record, appended to out; its pointers become ROOTS"""
    t = v.type; st = struct_of(t)
    a = int(v.address) if v.address else None
    out.append({"name": sym.name, "type": str(t), "addr": a,
                "value": int(v) if (is_ptr(t) or scalar(t)) else None,
                "kind": "ptr" if is_ptr(t) else ("int" if scalar(t) else "other"),
                "struct": st,
                "size": t.sizeof, "bytes": raw(a, t.sizeof),
                "arg": bool(sym.is_argument),      # parameters start with real values
                "target": str(t.strip_typedefs().target()) if is_ptr(t) else None,   # one star down
                "decl": sym.line})                 # the line it was declared on
    d = ptr_desc(t)
    if d and is_ptr(t): ROOTS.append((int(v), d))
    if is_rec(t):                                        # a struct on the stack: its fields, nested ones too
        out[-1]["fields"] = fields_of(v, t)
        for p, pd in ptr_values(v, t):                     # and what its pointers lead to: a list_head on the stack is a list's head
            if p and pd: ROOTS.append((p, pd))
    at = t.strip_typedefs()
    if at.code == gdb.TYPE_CODE_ARRAY:
        et = at.target().strip_typedefs(); ed = ptr_desc(et)
        if ed and et.code == gdb.TYPE_CODE_PTR:            # int *ps[3]: each element can lead to a heap block
            for k in range(min(at.sizeof // 8, 64)): ROOTS.append((int(v[k]), ed))
        base = at
        while base.code == gdb.TYPE_CODE_ARRAY: base = base.target().strip_typedefs()
        if base.code == gdb.TYPE_CODE_STRUCT:                # struct pair a[5]: what each element holds
            out[-1]["elem_fields"] = [{"name": f.name, "type": str(f.type), "offset": f.bitpos // 8, "size": f.type.sizeof,
                                       "kind": "ptr" if is_ptr(f.type) else ("int" if scalar(f.type) else "other")}
                                      for f in base.fields() if f.name]
            out[-1]["elem_size"] = base.sizeof

def collect_vars(frame):
    out, block = [], frame.block()
    while block and not block.is_static:
        for sym in block:
            if not (sym.is_variable or sym.is_argument): continue
            try: var_entry(out, sym, sym.value(frame))
            except gdb.error: pass
        if block.function: break
        block = block.superblock
    return out

def collect_globals():
    """our file's global and static variables, in the same shape as a frame's"""
    out = []
    try: st = gdb.selected_frame().find_sal().symtab
    except gdb.error: return out
    if not st: return out
    for blk in (st.global_block(), st.static_block()):
        for sym in blk:
            if not sym.is_variable or not sym.symtab or sym.symtab.filename != our_file: continue
            try: var_entry(out, sym, sym.value())
            except gdb.error: pass
    for v in out: v["global"] = True
    return out

def our_types():
    """the struct and union types our own file defines"""
    out, seen = [], set()
    try: st = gdb.selected_frame().find_sal().symtab
    except gdb.error: return out
    for sym in st.static_block():
        try:
            if sym.addr_class != gdb.SYMBOL_LOC_TYPEDEF or not sym.symtab or sym.symtab.filename != our_file: continue
            t = sym.type.strip_typedefs(); k = sname(sym.type)
            if t.code in (gdb.TYPE_CODE_STRUCT, gdb.TYPE_CODE_UNION) and k not in seen and t.sizeof: seen.add(k); out.append((k, t))
        except (gdb.error, RuntimeError): pass
    return out

def field_path(t, off, tname):
    """the field of struct t at byte offset off whose type is tname, as a path like "list" or "a.list", or None"""
    for f in t.strip_typedefs().fields():
        if f.name is None: continue
        fo, ft = f.bitpos // 8, f.type.strip_typedefs()
        if fo == off and str(ft.unqualified()) == tname: return f.name
        if is_rec(ft) and fo <= off < fo + ft.sizeof:
            sub = field_path(ft, off - fo, tname)
            if sub: return f.name + "." + sub
    return None

def container(p, tname):
    """p points INTO a used heap chunk, at a tname: (chunk start, the struct of ours that holds a tname there), or None"""
    for c, size in USED:
        if c < p < c + size: break
    else: return None
    want = REQ.get(c, size); best = None
    for k, t in OUR_TYPES:
        if t.sizeof > size or not field_path(t, p - c, tname): continue
        if best is None or abs(t.sizeof - want) < abs(best[1].sizeof - want): best = (k, t)   # the one closest to what was malloc'd
    return (c, best[0]) if best is not None else None

def signature(frame):
    """the function's C signature, like: void remove_elements_ref(struct ListNode **head, int val)"""
    try:
        blk = frame.block()
        while blk and not blk.function: blk = blk.superblock
        join = lambda t, n: t + ("" if t.endswith("*") else " ") + n
        ps = [join(str(sym.type), sym.name) for sym in blk if sym.is_argument]
        return "%s(%s)" % (join(str(frame.function().type.target()), frame.name()), ", ".join(ps))
    except (gdb.error, AttributeError, RuntimeError): return None

def returned(name):
    """what function `name` just handed back: on x86-64 it's still in rax, so read it as the return type"""
    try:
        sym = gdb.lookup_global_symbol(name) or gdb.lookup_symbol(name)[0]
        rt = sym.type.target()
        if rt.code == gdb.TYPE_CODE_VOID: return None
        return {"func": name, "type": str(rt), "value": int(gdb.parse_and_eval("$rax").cast(rt))}
    except (gdb.error, AttributeError, TypeError, RuntimeError): return None

def discover(roots, starts, locals_):
    """remember every block reachable from these pointers, following each pointer field by its own type.
       Structs first, then int and char arrays, so a struct is never read as an array of its first field.
       starts: where real malloc'd blocks start (None if the memory map can't be read), so leftover pointers can't invent one"""
    real = lambda a: a not in locals_ and (starts is None or a in starts)
    queue = [r for r in roots if r[1][0] == "struct"]
    arrays = [r for r in roots if r[1][0] == "array"]
    seen = set()
    while queue or arrays:
        while queue:
            addr, d = queue.pop(0)
            if not addr or addr in seen or addr in FREED: continue
            if addr in KNOWN: d = KNOWN[addr]                  # known already: still follow its fields, they may be new
            elif len(KNOWN) >= NODE_MAX: continue
            elif not real(addr):
                c = d[0] == "struct" and starts is not None and container(addr, d[1])
                if c and c[0] not in seen: queue.append((c[0], ("struct", c[1])))   # &item->list: the item that holds it
                continue
            if d[0] != "struct": continue
            seen.add(addr)
            try: b = read_block(addr, d[1])
            except gdb.error: continue
            KNOWN[addr] = d
            try:
                t = lookup(d[1])
                ps = list(ptr_values(gdb.Value(addr).cast(t.pointer()).dereference(), t))   # pointers in nested structs too
            except gdb.error: ps = []
            for p, fk in ps:
                if p and fk: (queue if fk[0] == "struct" else arrays).append((p, fk))
        while arrays:                                          # an int *, char * or int ** at the start of a used chunk
            addr, d = arrays.pop(0)
            if not addr or addr in seen or addr in FREED: continue
            if addr not in KNOWN:
                if len(KNOWN) >= NODE_MAX or not starts or addr not in starts: continue
                KNOWN[addr] = d
            d = KNOWN[addr]; seen.add(addr)
            if d[0] == "array" and len(d) > 3 and d[3]:            # a pointer array: each element can be a row of its own
                n = REQ.get(addr, max(0, chunk_size(addr) - 8)) // 8
                for p in words(addr, min(n, 512)):
                    if p: (queue if d[3][0] == "struct" else arrays).append((p, d[3]))

def heap_now():
    """every block we have ever seen — freed ones too, with their bytes as they are now"""
    out = []
    for addr, d in KNOWN.items():
        try: b = read_block(addr, d[1]) if d[0] == "struct" else read_array(addr, d[1], d[2])
        except gdb.error: continue
        b["freed"] = addr in FREED
        out.append(b)
    return sorted(out, key=lambda b: b["addr"])

def heap_bounds():
    """start and end of the [heap] mapping, or None before the first malloc"""
    try:
        with open("/proc/%d/maps" % gdb.selected_inferior().pid) as fh:
            for line in fh:
                if line.rstrip().endswith("[heap]"):
                    lo, hi = line.split()[0].split("-")
                    return int(lo, 16), int(hi, 16)
    except (IOError, ValueError): pass
    return None

def buffer_of(stream):
    """where stdin's or stdout's buffer is: FILE._IO_buf_base, offset 0x38 on x86-64 glibc"""
    try: return int(gdb.parse_and_eval("*(long *)(*(char **) &%s + 0x38)" % stream))
    except gdb.error: return 0

def chunks_now():
    """walk the heap chunk by chunk, using each chunk's size field"""
    b = heap_bounds()
    if not b: return []
    lo, hi = b
    bufs = {buffer_of("stdout"): "stdout", buffer_of("stdin"): "stdin"}
    out, p = [], lo
    while p + 16 <= hi and len(out) < CHUNK_MAX:
        try: size = int.from_bytes(bytes(gdb.selected_inferior().read_memory(p + 8, 8)), "little") & ~7
        except gdb.error: break
        if size < 32 or p + size > hi: break                 # not a sane chunk: stop walking
        user = p + 16
        if p + size == hi: state = "top"                     # the rest of the heap: not allocated
        elif user in FREED: state = "freed"
        else: state = "used"
        what = "tcache" if p == lo and size in (0x250, 0x290) else bufs.get(user)
        if not what and state == "used" and user not in ALLOCED: what = "malloc"   # malloc's own, never handed to you
        out.append({"addr": user, "size": size, "state": state, "what": what})
        if state == "top": break
        p += size
    return out

def in_our_file():
    try: return ours(gdb.selected_frame())
    except gdb.error: return False

def console():
    try:
        with open(STDOUT) as fh: return fh.read()
    except IOError: return ""

def maps_of(a):
    """(permissions, path) of the memory mapping that holds address a"""
    try:
        with open("/proc/%d/maps" % gdb.selected_inferior().pid) as fh:
            for line in fh:
                p = line.split(); lo, hi = (int(x, 16) for x in p[0].split("-"))
                if lo <= a < hi: return p[1], (p[5] if len(p) > 5 else "")
    except (IOError, ValueError): pass
    return None

def literal(a):
    """a char * into the program file (a string literal or a global): its text, up to 64 bytes"""
    m = maps_of(a)
    if not m or not m[1].startswith("/"): return None          # the stack, the heap, or anonymous memory
    try: b = bytes(gdb.selected_inferior().read_memory(a, 64))
    except gdb.error:
        b = b""
        for k in range(64):
            try: b += bytes(gdb.selected_inferior().read_memory(a + k, 1))
            except gdb.error: break
    end = b.find(b"\0")
    out = {"cstr": (b if end < 0 else b[:end]).decode("latin-1"), "cstr_ro": "w" not in m[0]}
    if end < 0: out["cstr_cut"] = True
    return out

def into(frames, glob, heap):
    """a pointer into the middle of a struct block (like &item->list): "into": {"addr": the block, "field": "list"}"""
    blocks = [b for b in heap if b.get("kind") != "array" and not b["freed"]]
    def mark(x, tname):
        p = x.get("value")
        if x.get("kind") != "ptr" or not p: return
        for b in blocks:
            if b["addr"] < p < b["addr"] + b["size"]:
                try: path = field_path(lookup(b["type"]), p - b["addr"], tname)
                except gdb.error: path = None
                if path: x["into"] = {"addr": b["addr"], "field": path}
                return
    def walk(fs):
        for f in fs or []:
            mark(f, (f.get("target") or "").strip()); walk(f.get("fields"))
    for v in [v for fr in frames for v in fr["vars"]] + glob:
        mark(v, (v.get("target") or "").strip()); walk(v.get("fields"))
    for b in blocks: walk(b["fields"])

def snapshot():
    del ROOTS[:]
    frame = gdb.selected_frame(); sal = frame.find_sal()
    frames, f = [], frame
    while f:
        s = f.find_sal()
        if s.symtab and s.symtab.filename == our_file:
            fr = {"func": f.name(), "at": s.line, "sig": signature(f), "vars": collect_vars(f)}
            fr.update(frame_mem(f, fr["vars"]))                    # return address, saved rbp, unused slots
            frames.append(fr)
        f = f.older()
    chunks = chunks_now()
    starts = {c["addr"] for c in chunks if c["state"] == "used"}       # where real malloc'd blocks start
    del USED[:]; USED.extend((c["addr"], c["size"] - 8) for c in chunks if c["state"] == "used")
    glob = collect_globals()
    locals_ = {v["addr"] for fr in frames for v in fr["vars"] if v["addr"]} | {v["addr"] for v in glob if v["addr"]}   # stack and global variables are never heap blocks
    seen_heap = chunks or maps_of(int(frame.read_register("rsp")))   # no heap yet: then only structs on the stack can be blocks
    discover(ROOTS, starts if seen_heap else None, locals_)
    for fr in frames:                                          # char * to a string literal: its text
        for v in fr["vars"]:
            if v["kind"] == "ptr" and v["value"] and re.sub(r"\b(const|volatile)\b", "", v["target"] or "").strip() in ("char", "signed char", "unsigned char"):
                lit = literal(v["value"])
                if lit: v.update(lit)
            if v["kind"] == "other" and v["bytes"] and re.match(r"^(?:const )?(?:signed |unsigned )?char \*\s*\[\d+\]$", v["type"]):   # char *words[3]
                b = bytes.fromhex(v["bytes"]); ws = [int.from_bytes(b[k:k + 8], "little") for k in range(0, len(b) - 7, 8)]
                lits = [literal(p) if p else None for p in ws[:64]]
                if any(lits): v["cstrs"] = [{"text": x["cstr"], "ro": x["cstr_ro"]} if x else None for x in lits]
    heap = heap_now()
    into(frames, glob, heap)
    ret = None
    if steps and len(frames) < len(steps[-1]["frames"]):           # a function just returned
        ret = returned(steps[-1]["frames"][0]["func"])
    st = {"line": sal.line, "func": frame.name(), "frames": frames,
          "heap": heap, "chunks": chunks, "ret": ret, "out": console(),
          "lib": [c for c in LIBCALLS if c["writes"] or c["func"] in ALLOCS or c["partial"]]}   # what the watchpoints caught
    if glob: st["globals"] = glob
    if EVENTS: st["events"] = EVENTS[:]; del EVENTS[:]           # what went wrong on the line that just ran
    steps.append(st)
    del LIBCALLS[:]

class NoWatch(Exception): pass
class Crashed(Exception): pass
DIED = []                              # the signal that stopped the program, once it has

def on_stop(ev):
    """a signal (SIGSEGV, SIGABRT …): remember it, and for a bad address, which address"""
    if not isinstance(ev, gdb.SignalEvent): return
    e = {"kind": "signal", "name": ev.stop_signal}
    if ev.stop_signal in ("SIGSEGV", "SIGBUS"):
        try: e["addr"] = int(gdb.parse_and_eval("(unsigned long) $_siginfo._sifields._sigfault.si_addr"))
        except (gdb.error, RuntimeError): pass
    EVENTS.append(e); DIED.append(e)

def crash_snapshot():
    """the program is dying: one last picture of your frames, on the line of yours that was running"""
    for e in EVENTS: e["pending"] = True
    snapshot()
    st = steps[-1]; f = gdb.selected_frame(); where = f.name()
    while f and not ours(f): f = f.older()                   # the newest frame in your file
    if f:
        st["line"], st["func"] = f.find_sal().line, f.name()
        st["crash"] = {"line": st["line"], "func": st["func"], "in": where}   # in: the function it died inside (raise, free …)

def run(cmd):
    try: t = gdb.execute(cmd, to_string=True)
    except gdb.error as e:
        if "Could not insert hardware" in str(e): raise NoWatch()
        raise
    if "Could not insert hardware" in t: raise NoWatch()    # gdb stopped half-way through the line

def advance():
    """run one line of your code; library code runs to the end without stopping"""
    run("step")
    if DIED: raise Crashed()
    while not in_our_file():
        run("finish")
        if DIED: raise Crashed()

gdb.execute("set pagination off"); gdb.execute("set confirm off")
gdb.execute("break " + START)
gdb.execute("run > %s 2>&1" % STDOUT)                    # stderr too: glibc says why it aborted there
our_file = gdb.selected_frame().find_sal().symtab.filename
OUR_TYPES = our_types()
try:
    gdb.execute("call (int) setvbuf(*(void **) &stdout, (char *) 0, 2, (unsigned long) 0)", to_string=True)
except gdb.error:
    pass
for fn in ("malloc", "calloc", "realloc"):
    try: Malloc(fn)
    except (gdb.error, RuntimeError): pass
Free()
for pc, fn, line in lib_calls():
    try: LibCall(pc, fn, line)
    except (gdb.error, RuntimeError): pass
gdb.events.stop.connect(on_stop)

for _ in range(MAX_STEPS):
    try:
        snapshot()
        try: advance()
        except NoWatch:                                     # this CPU can't: finish the line without watchpoints
            disarm(); watch_ok = False; del LIBCALLS[:]
            advance()
    except Crashed:                                         # a signal: the last picture, then stop
        disarm()
        try: crash_snapshot()
        except gdb.error: pass
        break
    except gdb.error:
        break
    finally:
        disarm()

if EVENTS and steps:                                         # the program died inside a line: what we saw goes on the last step
    steps[-1].setdefault("events", []).extend(dict(e, pending=True) for e in EVENTS); del EVENTS[:]
out = os.path.splitext(os.path.basename(gdb.current_progspace().filename))[0] + ".json"
with open(out, "w") as fh: json.dump({"file": our_file, "allocs_tracked": True, "watchpoints": watch_ok, "steps": steps}, fh)
print("wrote %s with %d steps" % (out, len(steps)))
