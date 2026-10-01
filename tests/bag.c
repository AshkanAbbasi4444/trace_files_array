#include <stdio.h>
#include <stdlib.h>

struct Bag {
  int *data;
  int size;
};

struct Bag* make_bag(int size) {
  printf("in make_bag\n");
  struct Bag* bag = malloc(sizeof(struct Bag));
  bag->data = calloc(size, sizeof(int));
  bag->size = size;
  return bag;
}

int main() {
  printf("in main\n");
  struct Bag* bag = make_bag(4);
  for (int i = 0; i < bag->size; i++) {
    bag->data[i] = 10 * (i + 1);
  }
  int *mid = bag->data + 2;
  printf("%d\n", *mid);
  free(bag->data);
  free(bag);
  return 0;
}
