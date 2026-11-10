/* Gateway admin login (fictional). Reads a password, checks it, then wipes
 * the buffer so the password doesn't stay in memory.
 * Written as an AI assistant might write it, to show a common failure pattern. */
#include <string.h>

int check_password(const char *pw);
void read_password(char *buf, size_t n);

int login(void)
{
    char pw[64];
    read_password(pw, sizeof pw);
    int ok = check_password(pw);
    memset(pw, 0, sizeof pw);   /* wipe the secret */
    return ok;
}
