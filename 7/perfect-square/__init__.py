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
    """perfect-square.cpp exists"""
    check50.exists("perfect-square.cpp")

@check50.check(exists)
def test_compile():
    """perfect-square.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG perfect-square.cpp -o perfect-square", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_example1():
    """outputs YES for 25"""
    check50.run("./perfect-square").stdin("25", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_example2():
    """outputs NO for 10"""
    check50.run("./perfect-square").stdin("10", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_one():
    """outputs YES for 1"""
    check50.run("./perfect-square").stdin("1", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_two():
    """outputs NO for 2"""
    check50.run("./perfect-square").stdin("2", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_large_square():
    """outputs YES for 999950884 (31622^2)"""
    check50.run("./perfect-square").stdin("999950884", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_large_non_square():
    """outputs NO for 999950885"""
    check50.run("./perfect-square").stdin("999950885", prompt=False).stdout("NO", regex=False).exit(0)



@check50.check(test_compile)
def test_random_yes():
    """handles random perfect square correctly"""
    val = random.randint(1, 31622)
    check50.run("./perfect-square").stdin(str(val * val), prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_random_no():
    """handles random non-perfect square correctly"""
    val = random.randint(2, 1000000)
    while int(val**0.5)**2 == val:
        val = random.randint(2, 1000000)
    check50.run("./perfect-square").stdin(str(val), prompt=False).stdout("NO", regex=False).exit(0)
