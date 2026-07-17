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
    """minimum-difference.cpp exists"""
    check50.exists("minimum-difference.cpp")

@check50.check(exists)
def test_compile():
    """minimum-difference.cpp compiles successfully"""
    check50.run("g++ -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG minimum-difference.cpp -o minimum-difference").exit(0)

@check50.check(test_compile)
def test_example1():
    """finds minimum difference correctly (Example 1)"""
    check50.run("./minimum-difference").stdin("6\n1 5 3 19 18 25", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test_example2():
    """finds minimum difference correctly (Example 2)"""
    check50.run("./minimum-difference").stdin("5\n4 9 1 32 13", prompt=False).stdout("3", regex=False).exit(0)

@check50.check(test_compile)
def test_duplicates():
    """handles arrays with duplicate values (difference of 0)"""
    check50.run("./minimum-difference").stdin("4\n5 12 5 20", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_negatives():
    """handles arrays with negative values"""
    check50.run("./minimum-difference").stdin("4\n-10 -5 0 5", prompt=False).stdout("5", regex=False).exit(0)

@check50.check(test_compile)
def test_mixed_longer():
    """handles longer mixed arrays"""
    check50.run("./minimum-difference").stdin("10\n15 3 27 8 9 30 21 22 5 100", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """finds minimum difference in random array correctly"""
    n = random.randint(10, 50)
    arr = [random.randint(-1000, 1000) for _ in range(n)]
    s_arr = sorted(arr)
    min_diff = min(s_arr[i+1] - s_arr[i] for i in range(n-1))
    expected = str(min_diff)
    stdin_data = f"{n}\n" + " ".join(map(str, arr))
    check50.run("./minimum-difference").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)
