#include <stdio.h>
#include <stdlib.h>

struct node {
  int val;
  struct node *next;
  struct node *link;
};

int main() {
  printf("in main\n");
  struct node *a = malloc(sizeof(struct node));
  struct node *b = malloc(sizeof(struct node));
  struct node *c = malloc(sizeof(struct node));
  struct node *d = malloc(sizeof(struct node));
  a->val = 1;
  b->val = 2;
  c->val = 3;
  d->val = 4;
  a->next = b;
  b->next = c;
  c->next = d;
  d->next = NULL;
  a->link = c;
  b->link = a;
  c->link = c;
  d->link = NULL;
  struct node *head = a;
  for (struct node *p = head; p != NULL; p = p->next) {
    if (p->link != NULL) {
      printf("%d links to %d\n", p->val, p->link->val);
    }
  }
  free(a);
  free(b);
  free(c);
  free(d);
  return 0;
}
