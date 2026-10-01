#include <stdio.h>
#include <stdlib.h>

typedef struct {
  int *data;
  int size;
} Bag;

Bag *make_bag(int n) {
  printf("in make_bag\n");
  Bag *b = malloc(sizeof(Bag));
  b->data = malloc(n * sizeof(int));
  b->size = n;
  for (int i = 0; i < n; i++) {
    b->data[i] = i * 3;
  }
  return b;
}

int main() {
  printf("in main\n");
  Bag *b = make_bag(4);
  b->data[1] = 100;
  printf("%d %d\n", b->size, b->data[1]);
  free(b->data);
  free(b);
  return 0;
}
