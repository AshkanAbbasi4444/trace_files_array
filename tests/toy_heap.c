#include <stdlib.h>

struct node { int val; struct node *next; };

int main() {
  struct node *a = malloc(sizeof *a);
  a->val = 1;
  a->next = NULL;
  free(a);
  struct node *b = malloc(sizeof *b);
  b->val = 2;
  b->next = NULL;
  free(b);
  int x = b->val;
  return x;
}
