#include <stdio.h>
#include <stdlib.h>

int main() {
  printf("in main\n");
  int stack[4] = {1, 2, 3, 4};
  int *heap = malloc(5 * sizeof(int));
  for (int i = 0; i < 5; i++) {
    heap[i] = i;
  }
  int n = 5;
  heap[n] = 99;
  int j = 4;
  stack[j] = 7;
  printf("%d %d\n", heap[0], stack[0]);
  free(heap);
  return 0;
}
