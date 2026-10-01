#include <stdio.h>

int main() {
  printf("in main\n");
  int grid[2][3] = {{1, 2, 3}, {4, 5, 6}};
  int *ps[2] = {grid[0], grid[1]};
  for (int i = 0; i < 2; i++) {
    for (int j = 0; j < 3; j++) {
      grid[i][j] = grid[i][j] * 10;
    }
  }
  printf("%d %d\n", grid[1][2], ps[1][0]);
  return 0;
}
