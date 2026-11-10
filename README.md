# Value Pivot: practice files

These are the companion files for the book *Value Pivot*. Each chapter folder has the code the chapter reviews, the answer key and the author's checker. Every company, person, address and figure in these files is fictional.

## Before you run anything

This code has deliberate faults in it. That's the point: each chapter shows you a mistake and how to find it. So:

- Run it on your own computer, in a folder of its own, with nothing important nearby.
- Don't point it at real data, real servers or real accounts.
- Read a script before you run it. The book shows you how.

Chapter 15 has a clean-up script that deletes files. **Never run `ch15-infra/project/clean_build.sh` with the real `rm`.** The chapter shows it with a stand-in, `project/fakebin/rm`, that only prints what it would have deleted.

## What's in each chapter

| Folder | Chapter | You'll need |
|---|---|---|
| `ch03-reading` | 3. Reading code you didn't write | Python 3.10 or newer |
| `ch11-python` | 11. Python: the pipeline that passed every test | Python 3.10 or newer |
| `ch12-sql` | 12. SQL: where the money lives | Python 3.10 or newer (SQLite comes with it) |
| `ch13-js-ts` | 13. JavaScript and TypeScript: the types that weren't there | Node.js 22.18 or newer |
| `ch14-java-csharp` | 14. Java and C#: the enterprise, where equal isn't always equal | Java 21, and the .NET 10 SDK (it runs `overdue.cs` as a single file) |
| `ch15-infra` | 15. Infrastructure, pipelines and scripts | Python 3.10 or newer with PyYAML, and Bash |
| `ch16-systems` | 16. Systems: C, C++ and Go | A C compiler (gcc), Go 1.22 or newer, and Rust |
| `ch20-home` | 20. Local AI doesn't mean local code | Python 3.10 or newer |

Inside each folder:

- `project` is what the chapter starts from: the code that came back from the AI assistant, its tests and its data.
- `answer-key` is the fixed version. Don't open it until you've finished the chapter, or you're truly stuck.
- `tools` holds the author's checker, which reproduces every number and result the chapter quotes.

The chapter tells you which commands to run, and from which folder.

## About the checkers

The checkers were written for the author's own computer, which is Windows with Ubuntu running under WSL, and some of them name tool locations on that machine. On another set-up you may need to change a path or two, or run the commands from the chapter by hand. The code in `project` and `answer-key` doesn't depend on any of that.

The `tools/regression` folders in Chapters 13 and 15 keep a first attempt at each fix. They're there to show the fault in that attempt, not to be used.

## Checking your download

`SHA256SUMS.txt` lists a SHA-256 hash for every file. On Linux or under WSL, from this folder:

```bash
sha256sum -c SHA256SUMS.txt
```

## Licence

The code is under the MIT licence: see `LICENSE`.
