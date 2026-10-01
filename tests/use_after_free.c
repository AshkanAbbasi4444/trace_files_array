#include <stdio.h>
#include <stdlib.h>

int main() {
  printf("in main\n");
  int *score = malloc(sizeof(int));
  *score = 90;
  free(score);
  int late = *score;
  printf("%d\n", late);
  return 0;
}
