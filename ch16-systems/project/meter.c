/* Usage meter for Lumen Grid's smart-meter gateway (fictional).
 * Written as an AI assistant might write it, to show a common failure pattern.
 * Adds a reading to a running total, refusing any reading that would overflow. */
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

#define ERR_OVERFLOW (-1)

__attribute__((noinline))
int add_reading(int total, int amount, int *out)
{
    if (amount > 0 && total + amount < total)   /* overflow check */
        return ERR_OVERFLOW;
    *out = total + amount;
    return 0;
}

int main(int argc, char **argv)
{
    int total = argc > 1 ? atoi(argv[1]) : 1000;
    int amount = argc > 2 ? atoi(argv[2]) : 250;
    int result = 0;
    int rc = add_reading(total, amount, &result);
    if (rc == ERR_OVERFLOW) printf("refused: would overflow\n");
    else printf("new total: %d\n", result);
    return 0;
}
