#include <stdio.h>
#include <stdlib.h>

struct node {
  int val;
  struct node *left;
  struct node *right;
};

struct node *new_node(int val) {
  printf("in new_node\n");
  struct node *n = malloc(sizeof(struct node));
  n->val = val;
  n->left = NULL;
  n->right = NULL;
  return n;
}

void in_order(struct node *root) {
  printf("in in_order\n");
  if (root == NULL) {
    return;
  }
  in_order(root->left);
  printf("%d\n", root->val);
  in_order(root->right);
}

void free_tree(struct node *root) {
  printf("in free_tree\n");
  if (root == NULL) {
    return;
  }
  free_tree(root->left);
  free_tree(root->right);
  free(root);
}

int main() {
  printf("in main\n");
  struct node *root = new_node(4);
  root->left = new_node(2);
  root->right = new_node(6);
  root->left->left = new_node(1);
  root->left->right = new_node(3);
  root->right->left = new_node(5);
  root->right->right = new_node(7);
  in_order(root);
  free_tree(root);
  root = NULL;
  return 0;
}
