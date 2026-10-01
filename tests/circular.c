#include <stdio.h>
#include <stdlib.h>

struct node {
  int val;
  struct node *next;
};

struct node *new_node(int val) {
  printf("in new_node\n");
  struct node *n = malloc(sizeof(struct node));
  n->val = val;
  n->next = NULL;
  return n;
}

int main() {
  printf("in main\n");
  struct node *head = new_node(1);
  head->next = new_node(2);
  head->next->next = new_node(3);
  head->next->next->next = head;
  struct node *p = head;
  do {
    printf("%d ", p->val);
    p = p->next;
  } while (p != head);
  printf("\n");
  struct node *last = head->next->next;
  last->next = NULL;
  while (head != NULL) {
    struct node *next = head->next;
    free(head);
    head = next;
  }
  return 0;
}
