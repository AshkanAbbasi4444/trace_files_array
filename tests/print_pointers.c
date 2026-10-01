#include <stdio.h>

int main() {
  printf("in main\n");
  int value = 42;
  int *ptr = &value;
  int **pptr = &ptr;
  int *nothing = NULL;
  printf("value   = %d\n", value);
  printf("*ptr    = %d\n", *ptr);
  printf("**pptr  = %d\n", **pptr);
  printf("&value  = %p\n", (void *)&value);
  printf("ptr     = %p\n", (void *)ptr);
  printf("*pptr   = %p\n", (void *)*pptr);
  printf("&ptr    = %p\n", (void *)&ptr);
  printf("pptr    = %p\n", (void *)pptr);
  printf("nothing = %p\n", (void *)nothing);
  return 0;
}
