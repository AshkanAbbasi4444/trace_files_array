#include <stdio.h>
#include <stdlib.h>

struct ring {
  int buf[5];
  int n;
};

struct counts {
  int seen[20];
  int total;
};

void fill(struct ring *r, int start) {
  printf("in fill\n");
  for (int i = 0; i < 5; i++) {
    r->buf[i] = start + i;
  }
  r->n = 5;
}

int main() {
  printf("in main\n");
  struct ring local;
  local.n = 0;
  for (int i = 0; i < 5; i++) {
    local.buf[i] = i * i;
    local.n++;
  }
  struct ring *heap = malloc(sizeof(struct ring));
  fill(heap, 10);
  heap->buf[2] = local.buf[4];
  struct counts c;
  c.total = 0;
  for (int i = 0; i < 20; i += 3) {
    c.seen[i] = 1;
    c.total++;
  }
  printf("%d %d %d\n", local.n, heap->buf[2], c.total);
  free(heap);
  return 0;
}
