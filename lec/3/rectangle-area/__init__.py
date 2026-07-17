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
    """rectangle-area.cpp exists"""
    check50.exists("rectangle-area.cpp")

@check50.check(exists)
def test_compile():
    """rectangle-area.cpp compiles successfully"""
    check50.run("g++ rectangle-area.cpp -o rectangle-area").exit(0)

@check50.check(test_compile)
def test_example():
    """handles input: 4 and 5"""
    check50.run("./rectangle-area").stdin("4", prompt=False).stdin("5", prompt=False).stdout("Area = 20", regex=False).exit(0)

@check50.check(test_compile)
def test_another():
    """handles input: 10 and 15"""
    check50.run("./rectangle-area").stdin("10", prompt=False).stdin("15", prompt=False).stdout("Area = 150", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random inputs correctly"""
    h = random.randint(1, 100)
    w = random.randint(1, 100)
    expected = f"Area = {h * w}"
    check50.run("./rectangle-area").stdin(str(h), prompt=False).stdin(str(w), prompt=False).stdout(expected, regex=False).exit(0)
