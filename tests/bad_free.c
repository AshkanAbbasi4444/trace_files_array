#include <stdio.h>
#include <stdlib.h>

int main() {
  printf("in main\n");
  int count = 5;
  int *p = &count;
  printf("count = %d\n", *p);
  free(p);
  printf("not reached\n");
  return 0;
}
