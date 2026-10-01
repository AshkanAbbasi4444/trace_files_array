#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>

struct list_head {
  struct list_head *next;
  struct list_head *prev;
};

#define LIST_HEAD(name) struct list_head name = { &(name), &(name) }
#define container_of(ptr, type, member) ((type *)((char *)(ptr) - offsetof(type, member)))

struct item {
  int val;
  struct list_head list;
};

LIST_HEAD(global_items);

void INIT_LIST_HEAD(struct list_head *h) {
  printf("in INIT_LIST_HEAD\n");
  h->next = h;
  h->prev = h;
}

void list_add_tail(struct list_head *n, struct list_head *h) {
  printf("in list_add_tail\n");
  struct list_head *last = h->prev;
  n->next = h;
  n->prev = last;
  last->next = n;
  h->prev = n;
}

void list_del(struct list_head *n) {
  printf("in list_del\n");
  n->prev->next = n->next;
  n->next->prev = n->prev;
  n->next = NULL;
  n->prev = NULL;
}

struct item *new_item(int val) {
  printf("in new_item\n");
  struct item *it = malloc(sizeof(struct item));
  it->val = val;
  INIT_LIST_HEAD(&it->list);
  return it;
}

int main() {
  printf("in main\n");
  struct list_head items;
  INIT_LIST_HEAD(&items);
  struct item *a = new_item(10);
  struct item *b = new_item(20);
  struct item *c = new_item(30);
  list_add_tail(&a->list, &items);
  list_add_tail(&b->list, &items);
  list_add_tail(&c->list, &items);
  list_del(&b->list);
  struct item *g = new_item(99);
  list_add_tail(&g->list, &global_items);
  for (struct list_head *p = items.next; p != &items; p = p->next) {
    struct item *it = container_of(p, struct item, list);
    printf("%d ", it->val);
  }
  printf("\n");
  free(a);
  free(b);
  free(c);
  free(g);
  return 0;
}
