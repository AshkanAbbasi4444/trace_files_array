#include <stdio.h>
#include <stdlib.h>

int **make_ragged(int n, int **returnColumnSizes) {
  printf("in make_ragged\n");
  int **rows = malloc(n * sizeof(int *));
  int *colSize = malloc(n * sizeof(int));
  for (int i = 0; i < n; i++) {
    colSize[i] = i + 1;
    rows[i] = malloc(colSize[i] * sizeof(int));
    for (int j = 0; j < colSize[i]; j++) {
      rows[i][j] = i + j;
    }
  }
  *returnColumnSizes = colSize;
  return rows;
}

int main() {
  printf("in main\n");
  int *colSize = NULL;
  int **rows = make_ragged(3, &colSize);
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < colSize[i]; j++) {
      printf("%d ", rows[i][j]);
    }
    printf("\n");
    free(rows[i]);
  }
  free(rows);
  free(colSize);
  return 0;
}
