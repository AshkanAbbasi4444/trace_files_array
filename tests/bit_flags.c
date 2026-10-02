#include <stdio.h>
#include <stdlib.h>

struct flags {
  unsigned on : 1;
  unsigned level : 3;
  unsigned mode : 4;
};

void show(struct flags f) {
  printf("in show\n");
  printf("on %u, level %u, mode %u\n", f.on, f.level, f.mode);
}

int main() {
  printf("in main\n");
  struct flags f;
  f.on = 1;
  f.level = 5;
  f.mode = 9;
  show(f);
  f.level = 2;
  f.on = 0;
  struct flags *h = malloc(sizeof(struct flags));
  h->on = 1;
  h->level = 7;
  h->mode = 3;
  show(*h);
  free(h);
  return 0;
}
