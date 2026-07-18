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
    """search.cpp exists"""
    check50.exists("search.cpp")

@check50.check(exists)
def test_compile():
    """search.cpp compiles successfully"""
    check50.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG search.cpp -o search 2>&1").exit(0)

@check50.check(test_compile)
def test1():
    """finds element that exists (Example 1)"""
    check50.run("./search").stdin("6 2\n1 2 3 4 5 6", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test2():
    """outputs notfound if element doesn't exist (Example 2)"""
    check50.run("./search").stdin("3 3\n5 22 1", prompt=False).stdout("notfound", regex=False).exit(0)

@check50.check(test_compile)
def test_first_element():
    """handles element found at first index (index 0)"""
    check50.run("./search").stdin("5 99\n99 2 3 4 5", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_last_element():
    """handles element found at last index (index N-1)"""
    check50.run("./search").stdin("5 99\n1 2 3 4 99", prompt=False).stdout("4", regex=False).exit(0)

@check50.check(test_compile)
def test_duplicate_target():
    """returns the first index if multiple copies of the target exist"""
    check50.run("./search").stdin("5 99\n1 99 3 99 5", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles edge case N = 1 (minimal size)"""
    check50.run("./search").stdin("1 99\n99", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1000():
    """handles N = 1000 with target at the very end"""
    stdin_data = "1000 99999\n" + " ".join(str(i) for i in range(1, 1000)) + " 99999"
    check50.run("./search").stdin(stdin_data, prompt=False).stdout("999", regex=False).exit(0)


@check50.check(test_compile)
def test_random():
    """finds index of target in a random array correctly"""
    n = random.randint(10, 50)
    arr = [random.randint(-1000, 1000) for _ in range(n)]
    if random.choice([True, False]):
        target = random.choice(arr)
        expected = str(arr.index(target))
    else:
        target = 9999
        expected = "notfound"
    stdin_data = f"{n} {target}\n" + " ".join(map(str, arr))
    check50.run("./search").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)
