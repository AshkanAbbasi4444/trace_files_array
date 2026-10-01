#include <stdio.h>

int main() {
  int squares[5];
  for (int i = 0; i < 5; i++) {
    squares[i] = i * i;
  }
  int last = squares[4];
  printf("%d\n", last);
  return 0;
}
