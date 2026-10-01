#include <stdio.h>
#include <stdlib.h>

void release(int *p) {
  printf("in release\n");
  free(p);
}

int main() {
  printf("in main\n");
  int *nums = malloc(3 * sizeof(int));
  nums[0] = 7;
  release(nums);
  free(nums);
  printf("not reached\n");
  return 0;
}
