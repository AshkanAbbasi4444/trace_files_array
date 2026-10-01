#include <stdio.h>
#include <stdlib.h>

struct point {
  int x;
  int y;
};

struct item2 {
  int val;
  struct point pos;
  struct item2 *next;
};

struct item2 *new_item(int val, int x, int y) {
  printf("in new_item\n");
  struct item2 *it = malloc(sizeof(struct item2));
  it->val = val;
  it->pos.x = x;
  it->pos.y = y;
  it->next = NULL;
  return it;
}

int main() {
  printf("in main\n");
  struct item2 *first = new_item(1, 10, 20);
  first->next = new_item(2, 30, 40);
  struct item2 local;
  local.val = 7;
  local.pos.x = 5;
  local.pos.y = 6;
  local.next = first;
  first->next->pos.y = 41;
  printf("%d %d\n", local.next->pos.x, first->next->pos.y);
  free(first->next);
  free(first);
  return 0;
}
