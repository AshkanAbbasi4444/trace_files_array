#include <stdio.h>

void swap(int *a, int i, int j) {
  int tmp = a[i];
  a[i] = a[j];
  a[j] = tmp;
}

int main() {
  int vals[4] = {10, 20, 30, 40};
  swap(vals, 0, 3);
  for (int i = 0; i < 2; i++) {
    printf("%d\n", vals[i]);
    swap(vals, i, i + 1);
  }
  return 0;
}
