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
  struct node *p = head;
  for (int i = 2; i <= 5; i++) {
    p->next = new_node(i);
    p = p->next;
  }
  struct node *tail = p;
  tail->next = head->next;
  p = head;
  for (int k = 0; k < 8; k++) {
    printf("%d ", p->val);
    p = p->next;
  }
  printf("\n");
  tail->next = NULL;
  while (head != NULL) {
    struct node *next = head->next;
    free(head);
    head = next;
  }
  return 0;
}
