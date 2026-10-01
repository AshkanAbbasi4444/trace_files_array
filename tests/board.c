#include <stdio.h>

int main() {
  printf("in main\n");
  char board[3][3];
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 3; j++) {
      board[i][j] = '.';
    }
  }
  board[1][2] = 'X';
  for (int i = 0; i < 3; i++) {
    printf("%c%c%c\n", board[i][0], board[i][1], board[i][2]);
  }
  return 0;
}
