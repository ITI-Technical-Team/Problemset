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
    """calculator.cpp exists"""
    check50.exists("calculator.cpp")

@check50.check(exists)
def test_compile():
    """calculator.cpp compiles successfully"""
    check50.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG calculator.cpp -o calculator 2>&1").exit(0)

@check50.check(test_compile)
def test_example():
    """handles input: 5 and 10"""
    check50.run("./calculator").stdin("5", prompt=False).stdin("10", prompt=False).stdout("5 + 10 = 15\n5 * 10 = 50\n5 - 10 = -5", regex=False).exit(0)

@check50.check(test_compile)
def test_negative():
    """handles negative numbers input: -3 and 4"""
    check50.run("./calculator").stdin("-3", prompt=False).stdin("4", prompt=False).stdout("-3 + 4 = 1\n-3 * 4 = -12\n-3 - 4 = -7", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random inputs correctly"""
    x = random.randint(1, 100)
    y = random.randint(1, 100)
    expected = f"{x} + {y} = {x + y}\n{x} * {y} = {x * y}\n{x} - {y} = {x - y}"
    check50.run("./calculator").stdin(str(x), prompt=False).stdin(str(y), prompt=False).stdout(expected, regex=False).exit(0)
