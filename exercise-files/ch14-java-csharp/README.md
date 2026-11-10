# Chapter 14 exercise files: Java and C#

Two exercises, one for each of the chapter's scenarios. Run `python check.py` in this folder to check your work, or `python check.py --end` to check the answers.

**What you need:**

- **14_01 (Java):** a Java Development Kit, 17 or newer, with `java` and `javac` on your PATH. The book used OpenJDK 21. The checker compiles your `Billing.java` together with a short test program of its own, and runs it.
- **14_02 (C#):** the .NET 10 SDK, with `dotnet` on your PATH. The checker runs your file the way the chapter does, as a file-based app: `dotnet run overdue.cs`. The first run takes a minute or so while .NET builds it.

If a toolchain is missing, its checks fail with a reason that says so, and the others still run.

**On Windows without Java:** if `java` and `javac` aren't on your PATH, the checker tries the author's set-up, a JDK at `/root/.local/jdk21` inside WSL Ubuntu.
