#include <stdlib.h>

struct node { int val; struct node *next; };

int main() {
  int vals[3] = {7, 8, 9};
  struct node *head = NULL;
  for (int i = 0; i < 3; i++) {
    struct node *n = malloc(sizeof *n);
    n->val = vals[i];
    n->next = head;
    head = n;
  }
  return 0;
}
