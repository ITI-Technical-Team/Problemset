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
    """reverse-array.cpp exists"""
    check50.exists("reverse-array.cpp")

@check50.check(exists)
def test_compile():
    """reverse-array.cpp compiles successfully"""
    check50.run("g++ -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG reverse-array.cpp -o reverse-array").exit(0)

@check50.check(test_compile)
def test_example():
    """reverses a typical array (Example 1)"""
    check50.run("./reverse-array").stdin("5\n2 6 9 7 3", prompt=False).stdout("3 7 9 6 2", regex=False).exit(0)

@check50.check(test_compile)
def test_single():
    """handles array of length 1"""
    check50.run("./reverse-array").stdin("1\n42", prompt=False).stdout("42", regex=False).exit(0)

@check50.check(test_compile)
def test_even():
    """handles an array of even length"""
    check50.run("./reverse-array").stdin("4\n10 20 30 40", prompt=False).stdout("40 30 20 10", regex=False).exit(0)

@check50.check(test_compile)
def test_duplicates():
    """handles duplicates: 1 1 5 1"""
    check50.run("./reverse-array").stdin("4\n1 1 5 1", prompt=False).stdout("1 5 1 1", regex=False).exit(0)

@check50.check(test_compile)
def test_longer():
    """handles a longer array with positive values"""
    check50.run("./reverse-array").stdin("10\n5 10 2 7 7 3 9 1 4 8", prompt=False).stdout("8 4 1 9 3 7 7 2 10 5", regex=False).exit(0)


@check50.check(test_compile)
def test_random():
    """reverses a random array correctly"""
    n = random.randint(10, 50)
    arr = [random.randint(-1000, 1000) for _ in range(n)]
    expected = " ".join(map(str, reversed(arr)))
    stdin_data = f"{n}\n" + " ".join(map(str, arr))
    check50.run("./reverse-array").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)
