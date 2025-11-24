# Tools — output checker

This folder contains a small helper script `output_checker.py` that runs a student program and compares stdout to an expected value.

Examples

From the problem directory (example `hello_cpp`):

```bash
# compile if needed
g++ -std=c++17 hello.cpp -o hello

# run checker with expected literal (strip whitespace/newlines first)
python3 ../../tools/output_checker.py --cmd "./hello" --expected "hello world" --strip

# or use an expected file
echo "hello world" > expected.txt
python3 ../../tools/output_checker.py --cmd "./hello" --expected-file expected.txt --strip --show-diff
```

Exit codes
- 0 — Accepted
- 1 — Wrong Answer (mismatch)
- 2 — Error running command or other problem (missing expected file, runtime error)

Notes
- The script runs commands in a shell, so be careful with untrusted inputs. It is intended for instructors and local testing.
- For CI integration, use the script in a job step and check its exit code to determine pass/fail.
