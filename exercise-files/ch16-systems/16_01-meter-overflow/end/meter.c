/* The fix: check before adding, so no overflow ever happens, or use the
 * compiler's checked-arithmetic builtin. Both are well defined. */
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

#define ERR_OVERFLOW (-1)

__attribute__((noinline))
int add_reading(int total, int amount, int *out)
{
    if (__builtin_add_overflow(total, amount, out))
        return ERR_OVERFLOW;
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
