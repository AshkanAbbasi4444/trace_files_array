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
| leak_array | realloc (copied part kept, the rest ??) and a leaked heap array |
| toy_fill, toy_swap, toy_walk, toy_big, toy_rec | stack arrays: fill loop, two i's, pointer walk, 20 elements, recursion |
| toy_mixed, toy_list, toy_heap | an array next to a linked list, linked lists, malloc reusing a freed block |

`../remove_element.json` was made by the older trace.py: it checks old traces still open the same.
