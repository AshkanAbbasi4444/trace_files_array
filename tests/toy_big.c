#include <stdio.h>

int main() {
  int big[20];
  for (int i = 0; i < 20; i++) {
    big[i] = i;
  }
  int k = 18;
  big[k] = -1;
  printf("%d\n", big[k]);
  return 0;
}
