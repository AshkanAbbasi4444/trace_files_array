#include <stdio.h>

struct pair {
  int val;
  int idx;
};

int main() {
  printf("in main\n");
  int vals[4] = {30, 10, 40, 20};
  struct pair a[4];
  for (int i = 0; i < 4; i++) {
    a[i].val = vals[i];
    a[i].idx = i;
  }
  printf("%d %d\n", a[2].val, a[2].idx);
  return 0;
}
