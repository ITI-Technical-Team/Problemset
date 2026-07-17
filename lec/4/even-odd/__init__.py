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
            expected_str = str(output).strip().lower()
            out = super().stdout(output=None).strip().lower()
            if out != expected_str:
                raise check50.Mismatch(expected_str, out)
            return self
        return super().stdout(output, *args, **kwargs)

check50.run = RobustRun

@check50.check()
def exists():
    """even-odd.cpp exists"""
    check50.exists("even-odd.cpp")

@check50.check(exists)
def test_compile():
    """even-odd.cpp compiles successfully"""
    check50.run("g++ even-odd.cpp -o even-odd").exit(0)

@check50.check(test_compile)
def test_two():
    """handles input: 2"""
    check50.run("./even-odd").stdin("2", prompt=False).stdout("Even", regex=False).exit(0)

@check50.check(test_compile)
def test_five():
    """handles input: 5"""
    check50.run("./even-odd").stdin("5", prompt=False).stdout("Odd", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random inputs correctly"""
    n = random.randint(-1000, 1000)
    expected = "Even" if n % 2 == 0 else "Odd"
    check50.run("./even-odd").stdin(str(n), prompt=False).stdout(expected, regex=False).exit(0)
