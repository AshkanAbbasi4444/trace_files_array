#include <stdio.h>

int main() {
  printf("in main\n");
  int a[5] = {10, 20, 30, 40, 50};
  int b[5];
  int n = 5;
  for (int i = 0; i < n; i++) {
    b[n - 1 - i] = a[i];
  }
  int sum = 0;
  for (int i = 0; i < n; i++) {
    sum += a[(i + 2) % n];
  }
  int pairs = 0;
  for (int i = 0; i < 3; i++) {
    pairs += a[2 * i] - a[i / 2];
  }
  int c[3] = {2, 0, 1};
  int x = 0;
  for (int i = 0; i < 3; i++) {
    x += c[c[i]];
  }
  printf("%d %d %d %d\n", b[0], sum, pairs, x);
  return 0;
}
