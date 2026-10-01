#include <stdio.h>

int total(int *a, int lo, int hi) {
  if (lo > hi) {
    return 0;
  }
  return a[lo] + total(a, lo + 1, hi);
}

int main() {
  int a[3] = {4, 5, 6};
  int s = total(a, 0, 2);
  printf("%d\n", s);
  return 0;
}
