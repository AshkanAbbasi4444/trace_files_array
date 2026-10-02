#include <stdio.h>

struct calc {
  int a;
  int b;
  int (*op)(int, int);
};

int add(int x, int y) {
  printf("in add\n");
  return x + y;
}

int mul(int x, int y) {
  printf("in mul\n");
  return x * y;
}

int main() {
  printf("in main\n");
  struct calc c;
  c.a = 6;
  c.b = 7;
  c.op = add;
  int r = c.op(c.a, c.b);
  printf("%d\n", r);
  c.op = mul;
  r = c.op(c.a, c.b);
  printf("%d\n", r);
  return 0;
}
