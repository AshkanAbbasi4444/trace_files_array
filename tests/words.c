#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
  printf("in main\n");
  char *words[] = {"cat", "dog", "bird"};
  int n = 3;
  char **copy = malloc(n * sizeof(char *));
  for (int i = 0; i < n; i++) {
    copy[i] = malloc(strlen(words[i]) + 1);
    strcpy(copy[i], words[i]);
  }
  copy[1][0] = 'f';
  for (int i = 0; i < n; i++) {
    printf("%s\n", copy[i]);
    free(copy[i]);
  }
  free(copy);
  return 0;
}
