#include <stdio.h>

int sum(int *a, int n) {
  printf("in sum\n");
  int total = 0;
  for (int i = 0; i < n; i++) {
    total += a[i];
  }
  return total;
}

int main() {
  printf("in main\n");
  int arr[8] = {1, 2, 3, 4, 5, 6, 7, 8};
  int s = sum(arr, 8);
  int *p = arr;
  p = arr + 1;
  printf("%p\n", (void *)arr);
  printf("%d %d\n", s, *p);
  return 0;
}
