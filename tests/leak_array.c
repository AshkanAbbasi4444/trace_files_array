#include <stdio.h>
#include <stdlib.h>

int* grow(int* a, int n) {
  printf("in grow\n");
  int* bigger = realloc(a, n * sizeof(int));
  for (int i = 3; i < n; i++) {
    bigger[i] = i;
  }
  return bigger;
}

int main() {
  printf("in main\n");
  int* a = malloc(3 * sizeof(int));
  a[0] = 7;
  a[1] = 8;
  a[2] = 9;
  a = grow(a, 12);
  int* lost = malloc(2 * sizeof(int));
  lost[0] = 1;
  lost = NULL;
  printf("%d\n", a[11]);
  free(a);
  return 0;
}
