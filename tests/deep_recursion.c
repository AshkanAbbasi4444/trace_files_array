#include <stdio.h>

int count_down(int n) {
  printf("in count_down\n");
  if (n == 0) {
    return 0;
  }
  return 1 + count_down(n - 1);
}

int main() {
  printf("in main\n");
  int depth = count_down(11);
  printf("%d\n", depth);
  return 0;
}
