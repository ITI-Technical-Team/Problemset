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
    """age-in-days.cpp exists"""
    check50.exists("age-in-days.cpp")

@check50.check(exists)
def test_compile():
    """age-in-days.cpp compiles successfully"""
    proc = check50.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG age-in-days.cpp -o age-in-days 2>&1")
    proc.stdout(output=None)
    proc.exit(0)

@check50.check(test_compile)
def test_400():
    """handles input: 400"""
    check50.run("./age-in-days").stdin("400", prompt=False).stdout("1 years\n1 months\n5 days", regex=False).exit(0)

@check50.check(test_compile)
def test_800():
    """handles input: 800"""
    check50.run("./age-in-days").stdin("800", prompt=False).stdout("2 years\n2 months\n10 days", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random inputs correctly"""
    n = random.randint(1, 10000)
    years = n // 365
    rem = n % 365
    months = rem // 30
    days = rem % 30
    expected = f"{years} years\n{months} months\n{days} days"
    check50.run("./age-in-days").stdin(str(n), prompt=False).stdout(expected, regex=False).exit(0)
