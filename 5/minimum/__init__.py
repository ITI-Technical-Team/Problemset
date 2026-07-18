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
    """minimum.cpp exists"""
    check50.exists("minimum.cpp")

@check50.check(exists)
def test_compile():
    """minimum.cpp compiles successfully"""
    proc = check50.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG minimum.cpp -o minimum 2>&1")
    proc.stdout(output=None)
    proc.exit(0)

@check50.check(test_compile)
def test1():
    """handles negatives: 3 -1 5 -13 -10"""
    check50.run("./minimum").stdin("5\n3 -1 5 -13 -10", prompt=False).stdout("-13", regex=False).exit(0)

@check50.check(test_compile)
def test2():
    """handles positives: 2 4 6 8"""
    check50.run("./minimum").stdin("4\n2 4 6 8", prompt=False).stdout("2", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles edge case N = 1 (minimal size)"""
    check50.run("./minimum").stdin("1\n999", prompt=False).stdout("999", regex=False).exit(0)

@check50.check(test_compile)
def test_all_zeroes():
    """handles edge case of all zeroes"""
    check50.run("./minimum").stdin("5\n0 0 0 0 0", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_duplicate_minimum():
    """handles duplicates of the minimum value"""
    check50.run("./minimum").stdin("5\n4 2 5 2 6", prompt=False).stdout("2", regex=False).exit(0)

@check50.check(test_compile)
def test_all_negative():
    """handles all negative elements"""
    check50.run("./minimum").stdin("4\n-10 -20 -30 -40", prompt=False).stdout("-40", regex=False).exit(0)


@check50.check(test_compile)
def test_random():
    """finds minimum in a random array correctly"""
    n = random.randint(10, 50)
    arr = [random.randint(-1000, 1000) for _ in range(n)]
    expected = str(min(arr))
    stdin_data = f"{n}\n" + " ".join(map(str, arr))
    check50.run("./minimum").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)
