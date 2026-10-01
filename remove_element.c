#include <stdio.h>

int removeElement(int* nums, int numsSize, int val) {
  printf("in removeElement\n");
  int k = 0;
  for (int i = 0; i < numsSize; i++) {
    if (nums[i] != val) {
      nums[k] = nums[i];
      k++;
    }
  }
  return k;
}

int main() {
  printf("in main\n");
  int nums[] = {0, 1, 2, 2, 3, 0, 4, 2};
  int k = removeElement(nums, 8, 2);
  printf("k = %d\n", k);
  for (int i = 0; i < k; i++) {
    printf("%d ", nums[i]);
  }
  printf("\n");
  return 0;
}
