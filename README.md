Clone

```bash
git clone <your-repo-url>
cd Week1
```

Optional (venv)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Solve a problem

1. Edit the problem file under `problems/<problem-name>/`.
2. Build/run locally:

C++ example:
```bash
cd problems/hello
g++ -std=c++17 hello.cpp -o hello
./hello
```

Check (use either):

Output checker (recommended):
```bash
cd problems/hello_cpp
python3 ../../tools/output_checker.py --cmd "./hello" --expected "hello world" --strip
```

check50 (optional):
```bash
check50 --local ./problems/hello_cpp/tests/check50.py
# or
python3 -m check50 --local ./problems/hello_cpp/tests/check50.py
```

Result
- `ACCEPTED` → exit code 0
- `WRONG ANSWER` → exit code 1 (use `--show-diff`)
