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

`../remove_element.json` was made by the older trace.py: it checks old traces still open the same.
