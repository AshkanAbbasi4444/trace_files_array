#include <stdio.h>

int main() {
  printf("in main\n");
  int a[6] = {3, 8, 1, 9, 4, 7};
  int lo = 0;
  int hi = 5;
  while (lo < hi) {
    int mid = lo + (hi - lo) / 2;
    printf("a[lo] = %d, a[hi] = %d, a[mid] = %d\n", a[lo], a[hi], a[mid]);
    lo++;
    hi--;
  }
  printf("lo = %d, hi = %d\n", lo, hi);
  return 0;
}
