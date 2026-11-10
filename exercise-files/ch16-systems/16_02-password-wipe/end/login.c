/* The fix: use a wipe the compiler is not allowed to remove. explicit_bzero
 * is provided by the GNU C Library (run here on 2.39); C23 adds memset_explicit for the same job. */
#define _DEFAULT_SOURCE
#include <string.h>

int check_password(const char *pw);
void read_password(char *buf, size_t n);

int login(void)
{
    char pw[64];
    read_password(pw, sizeof pw);
    int ok = check_password(pw);
    explicit_bzero(pw, sizeof pw);
    return ok;
}
