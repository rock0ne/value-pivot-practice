# 16_02: The password that stayed in memory

**Book:** Chapter 16, Scenario 2: the password that stayed in memory.

`login` reads the admin password, checks it, and then wipes the buffer with `memset`. Compiled at `-O2`, the wipe disappears from the machine code: `wipe calls=0 memset_calls=0`. Replace it with a wipe the compiler isn't allowed to remove. You're done when the `-O2` assembly still contains the call.

**Files:** `begin/login.c` (edit this). The answer is in `end/`: open it only when you've finished, or you're truly stuck.

**Check your work:** from the `ch16-systems` folder, run `python check.py`. The checker compiles `login.c` with `gcc -S` at `-O0` and `-O2` and searches the assembly, the way the chapter does.

**Hint:** the GNU C Library has a wipe that's always written. You may need `#define _DEFAULT_SOURCE` before the includes to use it.
