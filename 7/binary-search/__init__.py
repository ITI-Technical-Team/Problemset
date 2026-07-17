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
    """binary-search.cpp exists"""
    check50.exists("binary-search.cpp")

@check50.check(exists)
def test_compile():
    """binary-search.cpp compiles successfully"""
    check50.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG binary-search.cpp -o binary-search").exit(0)

@check50.check(test_compile)
def test_example1():
    """outputs correct YES/NO for multiple queries"""
    check50.run("./binary-search").stdin("5 3\n1 2 3 4 5\n5\n3\n6", prompt=False).stdout("YES\nYES\nNO", regex=False).exit(0)

@check50.check(test_compile, timeout=15)
def test_efficiency():
    """solution runs in time on large input (O(N*Q) solutions will exceed the time limit)"""
    # N=100000 elements, Q=10000 queries (all missing: -1).
    # Benchmarked WITHOUT fast I/O:
    #   O(Q log N) binary search: ~0.13s  -> well within the 2s timeout
    #   O(Q * N)  linear  search: ~6.00s  -> far exceeds the 2s timeout
    N, Q = 100000, 10000
    elements = " ".join(str(i) for i in range(1, N + 1))
    queries = "\n".join("-1" for _ in range(Q))
    stdin_content = f"{N} {Q}\n{elements}\n{queries}"
    expected_out = "\n".join("NO" for _ in range(Q))

    # Write input to a file to avoid pipe buffer deadlocks with large stdin.
    with open("efficiency_input.txt", "w") as f:
        f.write(stdin_content)

    # 'timeout 2' enforces a strict 2-second wall-clock limit on the student binary.
    # Exit code 124 means the process was killed -> check50 sees a non-zero exit.
    check50.run("timeout 2 ./binary-search < efficiency_input.txt").stdout(expected_out, regex=False).exit(0)

@check50.check(test_compile)
def test_edge_cases():
    """handles multiple binary search boundary edge cases"""
    # 1. N=1, Q=2 (found and missing)
    # 2. Target smaller than first element, larger than last element, at first, and at last element
    check50.run("./binary-search").stdin("1 2\n5\n5\n3", prompt=False).stdout("YES\nNO", regex=False).exit(0)
    check50.run("./binary-search").stdin("5 4\n10 20 30 40 50\n5\n55\n10\n50", prompt=False).stdout("NO\nNO\nYES\nYES", regex=False).exit(0)


@check50.check(test_compile)
def test_random():
    """performs binary search queries on sorted array correctly"""
    n = random.randint(10, 50)
    q = random.randint(5, 15)
    arr = sorted([random.randint(-1000, 1000) for _ in range(n)])
    queries = []
    expected_list = []
    for _ in range(q):
        if random.choice([True, False]):
            target = random.choice(arr)
            queries.append(target)
            expected_list.append("YES")
        else:
            target = random.randint(-1000, 1000)
            queries.append(target)
            expected_list.append("YES" if target in arr else "NO")
    expected = "\n".join(expected_list)
    stdin_data = f"{n} {q}\n" + " ".join(map(str, arr)) + "\n" + "\n".join(map(str, queries))
    check50.run("./binary-search").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)
