#include <stdio.h>
#include <stdlib.h>

int* make_squares(int n, int* returnSize) {
  printf("in make_squares\n");
  int* squares = malloc(n * sizeof(int));
  for (int i = 0; i < n; i++) {
    squares[i] = i * i;
  }
  *returnSize = n;
  return squares;
}

int main() {
  printf("in main\n");
  int size = 0;
  int* sq = make_squares(5, &size);
  for (int i = 0; i < size; i++) {
    printf("%d ", sq[i]);
  }
  printf("\n");
  free(sq);
  return 0;
}
