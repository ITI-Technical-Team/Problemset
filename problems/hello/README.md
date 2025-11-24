cd problems/hello

Compile:
```bash
g++ -std=c++17 hello.cpp -o hello
```

Run:
```bash
./hello
```

Check:
```bash
python3 ../../tools/output_checker.py --cmd "./hello" --expected "hello world" --strip
```

Or with check50:
```bash
check50 --local ./problems/hello/tests/check50.py
```
# Problem: Hello (C++)

Objective
- Write a C++ program that prints exactly: hello world

Files
- `hello.cpp` — your solution file. A template exists in the repository.

Quick student steps (copy/paste)

1. Change to the problem directory

```bash
cd problems/hello_cpp
```

2. Implement `hello.cpp` (a template is already provided). Build and run locally to sanity-check:

```bash
g++ -std=c++17 hello.cpp -o hello
./hello
```

3. Use the repository output checker to verify your program's stdout (from the problem folder):

```bash
# run checker and force colored badge for demo purposes
python3 ../../tools/output_checker.py --cmd "./hello" --expected "hello world" --strip --force-badge
```

4. (Optional) Run the `check50` tests if you prefer that system (requires `check50`):

```bash
# from repository root
check50 --local ./problems/hello_cpp/tests/check50.py
# or
python3 -m check50 --local ./problems/hello_cpp/tests/check50.py
```

Interpreting results
- The output checker prints `ACCEPTED` (exit code 0) or `WRONG ANSWER` (exit code 1). Use `--show-diff` to view the mismatch.
- `check50` provides a per-test report; passing all tests means the problem is accepted.

Notes
- Use `--strip` when comparing outputs that may contain trailing newlines or whitespace.
