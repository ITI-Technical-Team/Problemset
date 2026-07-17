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
    """min-function.cpp exists"""
    check50.exists("min-function.cpp")

@check50.check(exists)
def test_compile():
    """min-function.cpp compiles successfully"""
    check50.run("g++ min-function.cpp -o min-function").exit(0)

@check50.check(test_compile)
def test_example():
    """handles input: 3 5"""
    check50.run("./min-function").stdin("3", prompt=False).stdin("5", prompt=False).stdout("3", regex=False).exit(0)

@check50.check(test_compile)
def test_negative():
    """handles input: 10 -2"""
    check50.run("./min-function").stdin("10", prompt=False).stdin("-2", prompt=False).stdout("-2", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random inputs correctly"""
    x = random.randint(-1000, 1000)
    y = random.randint(-1000, 1000)
    expected = str(min(x, y))
    check50.run("./min-function").stdin(str(x), prompt=False).stdin(str(y), prompt=False).stdout(expected, regex=False).exit(0)
