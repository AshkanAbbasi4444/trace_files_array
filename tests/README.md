# Toy programs for the viewer

Small C programs and their traces, to re-check `node_cards_viewer.html` and `trace.py`.

- `./run_traces.sh` rebuilds every `*.c` here (`gcc -g -O0`) and traces it with `gdb -q -batch -x ../trace.py`;
  `./run_traces.sh bag.c` does just one.
- Open the viewer, drop in `name.json` and `name.c`, and step through.

| program | checks |
|---|---|
| make_squares | malloc'd int array returned to main, `int *returnSize` arrow to main's int, free |
| bag | `struct Bag { int *data; int size; }`: the data field's arrow into a calloc'd array, `mid = data + 2` |
| heap_string | malloc(6) + strcpy: char slots with `\0`, strcpy's watchpoint marks, read-only string literal |
| out_of_bounds | heap[5] and stack[4] written past the end: the red banners and the memory view |
| index_exprs | b[n-1-i], a[(i+2)%n], a[2*i], a[i/2], c[c[i]] |
| print_pointers | the printf panel: value, *ptr, **pptr, &value, ptr, *pptr, &ptr, pptr and a NULL pointer, against what the program printed |
| leak_array | realloc (copied part kept, the rest ??) and a leaked heap array |
| toy_fill, toy_swap, toy_walk, toy_big, toy_rec | stack arrays: fill loop, two i's, pointer walk, 20 elements, recursion |
| toy_mixed, toy_list, toy_heap | an array next to a linked list, linked lists, malloc reusing a freed block |
| two_pointers | lo and hi walk inward (`while (lo < hi)`): the slots between them shaded, `mid` bold, then "empty range" when lo > hi |
| sliding_sum | `sum += a[i] - a[i - 3]`: the window between the two slots |
| tree | a 7-node tree with malloc, a recursive in-order print and a recursive free: root on top, NULL stubs, freed nodes keep their place |
| deep_recursion | 13 frames on the stack at once: the frames wrap into rows |
| grid | a 3x4 `int **` grid (row pointers, then each row): the column of row pointers, its arrows, `i→` and `↑j` |
| ragged | rows of length 1, 2 and 3 plus `int *colSize` filled through `int **returnColumnSizes` |
| words | `char *words[]` of string literals and a malloc'd `char **` copy: string rows, `copy[1][0] = 'f'` |
| board | `char board[3][3]` filled with '.', then one 'X': a char grid on the stack |
| pairs | `struct pair { int val; int idx; } a[4]` filled in a loop: a little card per slot, each field ?? until set |
| grid2d | `int grid[2][3]` and `int *ps[2] = {grid[0], grid[1]}`: a 2D grid on the stack and an arrow from each pointer slot |
| nested | `struct item2 { int val; struct point pos; struct item2 *next; }`: a malloc'd list of 2 and one on the stack, `it->pos.x`, `local.pos.y` |
| dlist | a 4-node doubly linked list built by hand, one node inserted in the middle and one deleted: next arrows below, prev above, `1 ⇄ 2 ⇄ 3`, the half-done links in red while it inserts |
| dlist_broken | the same list with `c->prev = a` (should be b): a red prev arrow and "0x300's prev doesn't point back to 0x200" |
| circular | a circular singly linked list of 3 nodes, walked with do/while, then cut and freed: `head: 1 → 2 → 3 → (back to 1)` and the last arrow curving back |
| rho | a 5-node list whose tail points back to node 2 (a "ρ"), walked 8 steps, then cut: `head: 1 → 2 → 3 → 4 → 5 → (back to 2)`, the loop arrow and "↻ loop start" |
| klist | kernel style: `struct list_head`, INIT_LIST_HEAD, list_add_tail, list_del, container_of with offsetof, `struct item { int val; struct list_head list; }`, a global LIST_HEAD and one on the stack |
| bag_typedef | `typedef struct { int *data; int size; } Bag;` with no struct name: the Bag card (it didn't show before) and its data array |
| fn_pointer | `struct calc { int a; int b; int (*op)(int, int); }`: `c.op = add`, `c.op(c.a, c.b)`, then `c.op = mul`: the field shows `→ add()`, click it to see add in the code; "Calls add through c.op" |
| ring | `struct ring { int buf[5]; int n; }` filled in a loop on the stack and malloc'd (and `int seen[20]` for "+4 more"): array fields as slots, `r->buf[2]` |
| double_free | frees the same block twice (once in a helper, once in main): the "free(0x100) a second time" banner on line 14; glibc aborts |
| bad_free | frees the address of a stack variable: the "that address never came from malloc" banner; glibc aborts |
| null_read | reads through a NULL next pointer: "Segmentation fault on line 12: tried to read address 0x0 (NULL): second was NULL", second outlined red |
| use_after_free | reads a block after free(): no crash, the use-after-free banner |
| heap_overflow_free | writes 3 ints past a 500-int block, then frees it: glibc aborts with "free(): invalid next size (normal)" |
| print200 | a loop that prints 200 lines: only the new output is stored per step (`out_add`); `print200.json.gz` opens in the viewer too |
| add | `int add(int a, int b)` called from main: turn on **assembly** in View to see each line's instructions and the registers (rsp and rbp move into add's frame and back) |
| add_insn | the same program traced with `STEP_INSN = True`: one step per machine instruction (open it with `add.c`); mid-line steps say "still running this line: instruction 3 of 4 ran" |

`../remove_element.json` was made by the older trace.py: it checks old traces still open the same.

Traces are written small: each step stores only the output that is new (`out_add`), and a frame, a heap block,
the chunk list or the globals that didn't change since the step before is just `{"same_as_prev": true}`.
The viewer puts it all back when it opens the trace, and also opens the `.json.gz` that trace.py writes next to it.
Set `COMPACT = False` at the top of trace.py for the full form. Sizes, every program here traced again:
all of them together went from 5.08 MB to 1.90 MB as .json, or 60 KB as .json.gz (tree.json: 1.28 MB → 209 KB → 4.4 KB).
With each line's machine code and the registers added, the full form of all of them is 7.08 MB, the small .json 2.72 MB
and the .json.gz 128 KB (tree: 1.24 MB → 247 KB → 7.4 KB; the same programs without them were 6.17 MB in full form).
The traces already in this folder keep their old, full form: they check that old traces still open the same.
print200, add, add_insn and null_read are traced with the newest trace.py (small form, plus the machine code and registers);
null_read's last step shows the instruction that crashed, `mov (%rax),%eax` with rax = 0.
