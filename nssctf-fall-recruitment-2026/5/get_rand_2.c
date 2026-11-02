#include <stdio.h>
#include <unistd.h>
#include <stdint.h>
#include <sys/random.h>
#include <string.h>
#include <stdlib.h>

int main()
{
    char rnd[8];
    getrandom(rnd, 8, 0);

    uint64_t input[5];
    memset(input, 0, 32); // rnd_input[0:3], excluding [4]

    ssize_t input_len = read(0, input, 0x1Fu);

    if ( input_len > 0 && *((char *)input + input_len - 1) == 10 ) {
        *((char *)input + input_len - 1) = 0;
    }

    for (int i = 0; i < 8; i++) {
        printf("%d ", (int)rnd[i]);
    }

    printf("\n");
}