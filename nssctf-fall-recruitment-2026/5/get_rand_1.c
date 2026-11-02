#include <stdio.h>
#include <stdlib.h>

int main() {
    unsigned int n1 = 0x1bf52,
                 n2 = 0x721;

    srand(n1);
    for (int i = 0; i < 3; i++) {
        rand();
    }
    unsigned int v3 = rand() % n2;

    printf("%u\n", v3);
}