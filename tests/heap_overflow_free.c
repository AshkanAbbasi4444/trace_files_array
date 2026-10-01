#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
  printf("in main\n");
  int *a = malloc(500 * sizeof(int));
  int *b = malloc(4 * sizeof(int));
  memset(a, 0, 500 * sizeof(int));
  for (int i = 500; i <= 502; i++) {
    a[i] = 1;
  }
  free(a);
  free(b);
  printf("not reached\n");
  return 0;
}
