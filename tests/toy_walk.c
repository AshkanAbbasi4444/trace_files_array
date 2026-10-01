#include <stdio.h>

int main() {
  int data[6] = {5, 6, 7, 8, 9, 10};
  int *p = data;
  int *end = data + 6;
  while (p < end) {
    *p = *p * 2;
    p++;
  }
  char word[8] = "hello";
  char *c = word;
  while (*c) {
    c++;
  }
  int far = 9;
  if (far < 6) {
    data[far] = 0;
  }
  printf("%d %s\n", data[0], word);
  return 0;
}
