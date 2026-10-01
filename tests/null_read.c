#include <stdio.h>
#include <stdlib.h>

struct node {
  int val;
  struct node *next;
};

int second_value(struct node *head) {
  printf("in second_value\n");
  struct node *second = head->next;
  return second->val;
}

int main() {
  printf("in main\n");
  struct node *head = malloc(sizeof(struct node));
  head->val = 1;
  head->next = NULL;
  int v = second_value(head);
  printf("%d\n", v);
  free(head);
  return 0;
}
