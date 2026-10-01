#include <stdio.h>
#include <stdlib.h>

struct dnode {
  int val;
  struct dnode *prev;
  struct dnode *next;
};

struct dnode *new_node(int val) {
  printf("in new_node\n");
  struct dnode *n = malloc(sizeof(struct dnode));
  n->val = val;
  n->prev = NULL;
  n->next = NULL;
  return n;
}

void free_all(struct dnode *head) {
  printf("in free_all\n");
  while (head != NULL) {
    struct dnode *next = head->next;
    free(head);
    head = next;
  }
}

int main() {
  printf("in main\n");
  struct dnode *a = new_node(1);
  struct dnode *b = new_node(2);
  struct dnode *c = new_node(3);
  struct dnode *d = new_node(4);
  a->next = b;
  b->prev = a;
  b->next = c;
  c->prev = a;
  c->next = d;
  d->prev = c;
  struct dnode *head = a;
  for (struct dnode *p = d; p != NULL; p = p->prev) {
    printf("%d ", p->val);
  }
  printf("\n");
  free_all(head);
  return 0;
}
