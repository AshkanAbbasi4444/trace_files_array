#include <stdio.h>
#include <stdlib.h>

struct tnode {
  int val;
  struct tnode *left;
  struct tnode *right;
  struct tnode *parent;
};

struct tnode *new_node(int val) {
  printf("in new_node\n");
  struct tnode *n = malloc(sizeof(struct tnode));
  n->val = val;
  n->left = NULL;
  n->right = NULL;
  n->parent = NULL;
  return n;
}

int main() {
  printf("in main\n");
  struct tnode *root = new_node(4);
  root->left = new_node(2);
  root->left->parent = root;
  root->right = new_node(6);
  root->right->parent = root;
  root->left->left = new_node(1);
  root->left->left->parent = root->left;
  root->left->right = new_node(3);
  root->left->right->parent = root->left;
  for (struct tnode *p = root->left->right; p != NULL; p = p->parent) {
    printf("%d\n", p->val);
  }
  free(root->left->left);
  free(root->left->right);
  free(root->left);
  free(root->right);
  free(root);
  return 0;
}
