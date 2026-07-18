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
    """compare-numbers.cpp exists"""
    check50.exists("compare-numbers.cpp")

@check50.check(exists)
def test_compile():
    """compare-numbers.cpp compiles successfully"""
    proc = check50.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG compare-numbers.cpp -o compare-numbers 2>&1")
    proc.stdout(output=None)
    proc.exit(0)

@check50.check(test_compile)
def test_less():
    """handles input: X = 5, Y = 10"""
    check50.run("./compare-numbers").stdin("5", prompt=False).stdin("10", prompt=False).stdout("X is less than Y", regex=False).exit(0)

@check50.check(test_compile)
def test_greater():
    """handles input: X = 10, Y = 5"""
    check50.run("./compare-numbers").stdin("10", prompt=False).stdin("5", prompt=False).stdout("X is greater than Y", regex=False).exit(0)

@check50.check(test_compile)
def test_equal():
    """handles input: X = 5, Y = 5"""
    check50.run("./compare-numbers").stdin("5", prompt=False).stdin("5", prompt=False).stdout("X is equal to Y", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random inputs correctly"""
    x = random.randint(-1000, 1000)
    y = random.randint(-1000, 1000)
    if x < y:
        expected = "X is less than Y"
    elif x > y:
        expected = "X is greater than Y"
    else:
        expected = "X is equal to Y"
    check50.run("./compare-numbers").stdin(str(x), prompt=False).stdin(str(y), prompt=False).stdout(expected, regex=False).exit(0)
