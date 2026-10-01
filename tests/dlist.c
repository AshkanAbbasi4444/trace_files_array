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

void insert_after(struct dnode *at, int val) {
  printf("in insert_after\n");
  struct dnode *n = new_node(val);
  n->prev = at;
  n->next = at->next;
  if (at->next != NULL) {
    at->next->prev = n;
  }
  at->next = n;
}

void delete_node(struct dnode **head, struct dnode *n) {
  printf("in delete_node\n");
  if (n->prev != NULL) {
    n->prev->next = n->next;
  } else {
    *head = n->next;
  }
  if (n->next != NULL) {
    n->next->prev = n->prev;
  }
  free(n);
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
  c->prev = b;
  c->next = d;
  d->prev = c;
  struct dnode *head = a;
  insert_after(b, 25);
  delete_node(&head, c);
  for (struct dnode *p = head; p != NULL; p = p->next) {
    printf("%d ", p->val);
  }
  printf("\n");
  free_all(head);
  head = NULL;
  return 0;
}
