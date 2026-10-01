#include <stdlib.h>

struct node { int val; struct node *next; };

int main() {
  struct node *head = NULL;
  for (int i = 0; i < 3; i++) {
    struct node *n = malloc(sizeof *n);
    n->val = i;
    n->next = head;
    head = n;
  }
  struct node *second = head->next;
  free(head);
  head = second;
  return 0;
}
