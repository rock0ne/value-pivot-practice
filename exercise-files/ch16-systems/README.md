# Chapter 16 exercise files: systems code

**Book:** Chapter 16. Systems: C, C++ and Go, where the compiler has the last word.

These exercises build real code, so they need the chapter's toolchains: GCC for 16_01 and 16_02, Go 1.22 or newer for 16_03, and Rust with cargo and Clippy for 16_04. The author ran them on Ubuntu 24.04 with GCC 13.3.0, Go 1.27.3 and Rust 1.99.1. What `-O2` removes depends on the compiler, so a different compiler can give different results.

**Linux:** install the toolchains, then run `python check.py` from this folder.

**macOS:** `check.py` runs directly, but `gcc` on a Mac is usually Clang, and the C results may differ from the book's. A Linux machine or VM is closer to the chapter.

**Windows:** the checks run inside WSL, in the distribution named `Ubuntu`. Install the toolchains there, then run `python check.py` from this folder in Windows as usual. To use a distribution with another name, set `VP_WSL_DISTRO` first, for example `set VP_WSL_DISTRO=Ubuntu-24.04`.

The checker looks for Go and Rust on the PATH, and also in `~/.local/go`, `~/.local/rust`, `~/go`, `~/.cargo` and `/usr/local/go`. If a toolchain is missing, the check says so instead of failing with an error. Go runs with `GOTOOLCHAIN=local` and no network, as in the chapter. Every build happens in a temporary folder that's deleted afterwards, so nothing is written into `begin/` or `end/`.

| Exercise | Book section |
|---|---|
| 16_01 The overflow check that wasn't there | Scenario 1: the overflow check that wasn't there |
| 16_02 The password that stayed in memory | Scenario 2: the password that stayed in memory |
| 16_03 meterd: the refused readings and the go line | Scenario 3 (Go) and Scenario 4 (Go) |
| 16_04 Rust billing: overflow and casts | Rust: the language to watch |
