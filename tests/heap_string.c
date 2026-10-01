#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
  printf("in main\n");
  const char *greeting = "hello";
  char *s = malloc(6);
  strcpy(s, greeting);
  s[0] = 'j';
  printf("%s\n", s);
  free(s);
  return 0;
}
