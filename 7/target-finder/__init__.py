import check50
import random

class RobustRun(check50.run):
    def __init__(self, *args, **kwargs):
        self._waited = False
        super().__init__(*args, **kwargs)

    def _wait(self, timeout=5):
        if self._waited:
            return self
        super()._wait(timeout)
        self._waited = True
        return self

    def stdout(self, output=None, *args, **kwargs):
        if output is not None and not kwargs.get("regex", True):
            expected_str = str(output)
            out = super().stdout(output=None)
            if out.split() != expected_str.split():
                raise check50.Mismatch(expected_str, out)
            return self
        return super().stdout(output, *args, **kwargs)

check50.run = RobustRun

@check50.check()
def exists():
    """target-finder.cpp exists"""
    check50.exists("target-finder.cpp")

@check50.check(exists)
def test_compile():
    """target-finder.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds target-finder.cpp -o target-finder", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_example1():
    """outputs correct YES/NO for the example case"""
    check50.run("./target-finder").stdin("5 3\n1 2 3 4 5\n4 5\n3 3\n1 6", prompt=False).stdout("YES\nNO\nYES", regex=False).exit(0)

@check50.check(test_compile)
def test_all_no():
    """outputs NO when the target does not exist in the array"""
    check50.run("./target-finder").stdin("3 1\n1 2 3\n10 3", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_all_yes():
    """outputs YES when the target exists in the array"""
    check50.run("./target-finder").stdin("5 1\n1 2 3 4 5\n4 9", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile, timeout=10)
def test_efficiency():
    """solution runs in time on sorted input (O(N * Q) naive will exceed the time limit)"""
    import os
    N, Q = 150000, 75000
    elements = " ".join(str(i) for i in range(1, N + 1))
    queries = "\n".join("1 300000" for _ in range(Q))
    stdin_content = f"{N} {Q}\n{elements}\n{queries}"

    sandbox_dir = os.path.dirname(os.path.abspath("./target-finder"))
    input_path = os.path.join(sandbox_dir, "efficiency_input.txt")
    with open(input_path, "w") as f:
        f.write(stdin_content)

    check50.run('bash -c "timeout 2 ./target-finder < efficiency_input.txt"').exit(0)


@check50.check(test_compile)
def test_random():
    """finds queries in sorted array correctly"""
    n = random.randint(10, 50)
    q = random.randint(5, 15)
    arr = sorted([random.randint(-1000, 1000) for _ in range(n)])
    queries_str = []
    expected_list = []
    for _ in range(q):
        x = random.randint(-1000, 1000)
        if random.choice([True, False]):
            val = random.choice(arr)
            z = val + x
            queries_str.append(f"{x} {z}")
            expected_list.append("YES")
        else:
            z = random.randint(-2000, 2000)
            target = z - x
            queries_str.append(f"{x} {z}")
            expected_list.append("YES" if target in arr else "NO")
    expected = "\n".join(expected_list)
    stdin_data = f"{n} {q}\n" + " ".join(map(str, arr)) + "\n" + "\n".join(queries_str)
    check50.run("./target-finder").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)
