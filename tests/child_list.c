#include <stdio.h>
#include <stdlib.h>

struct node {
  int val;
  struct node *next;
  struct node *child;
};

struct node *new_node(int val) {
  printf("in new_node\n");
  struct node *n = malloc(sizeof(struct node));
  n->val = val;
  n->next = NULL;
  n->child = NULL;
  return n;
}

int main() {
  printf("in main\n");
  struct node *head = new_node(1);
  head->next = new_node(2);
  head->next->next = new_node(3);
  head->next->next->next = new_node(4);
  struct node *two = head->next;
  two->child = new_node(5);
  two->child->next = new_node(6);
  struct node *four = two->next->next;
  four->child = new_node(7);
  four->child->next = new_node(8);
  for (struct node *p = head; p != NULL; p = p->next) {
    printf("%d", p->val);
    for (struct node *c = p->child; c != NULL; c = c->next) {
      printf(" %d", c->val);
    }
    printf("\n");
  }
  return 0;
}
