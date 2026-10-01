#include <stdio.h>

int main() {
  printf("in main\n");
  int total = 0;
  for (int i = 0; i < 200; i++) {
    total += i;
    printf("line %d, total %d\n", i, total);
  }
  return 0;
}
