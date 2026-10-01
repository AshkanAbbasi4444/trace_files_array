#include <stdio.h>

int main() {
  printf("in main\n");
  int a[8] = {1, 2, 3, 4, 5, 6, 7, 8};
  int sum = a[0] + a[1] + a[2];
  printf("sum = %d\n", sum);
  for (int i = 3; i < 8; i++) {
    sum += a[i] - a[i - 3];
    printf("sum = %d\n", sum);
  }
  return 0;
}
