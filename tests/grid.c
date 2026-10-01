#include <stdio.h>
#include <stdlib.h>

int main() {
  printf("in main\n");
  int rows = 3;
  int cols = 4;
  int **grid = malloc(rows * sizeof(int *));
  for (int i = 0; i < rows; i++) {
    grid[i] = malloc(cols * sizeof(int));
  }
  for (int i = 0; i < rows; i++) {
    for (int j = 0; j < cols; j++) {
      grid[i][j] = i * 10 + j;
    }
  }
  for (int i = 0; i < rows; i++) {
    for (int j = 0; j < cols; j++) {
      printf("%d ", grid[i][j]);
    }
    printf("\n");
  }
  for (int i = 0; i < rows; i++) {
    free(grid[i]);
  }
  free(grid);
  return 0;
}
