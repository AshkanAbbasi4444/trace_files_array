#include <stdio.h>

int add(int a, int b) {
  printf("in add\n");
  int sum = a + b;
  return sum;
}

int main() {
  printf("in main\n");
  int x = 3;
  int y = 4;
  int z = add(x, y);
  printf("%d\n", z);
  return 0;
}
