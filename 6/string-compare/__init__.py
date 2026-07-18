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
    """string-compare.cpp exists"""
    check50.exists("string-compare.cpp")

@check50.check(exists)
def test_compile():
    """string-compare.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG string-compare.cpp -o string-compare", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_example1():
    """handles input: 5 1"""
    check50.run("./string-compare").stdin("5 1", prompt=False).stdout("Greater", regex=False).exit(0)

@check50.check(test_compile)
def test_example2():
    """handles input: 5 5"""
    check50.run("./string-compare").stdin("5 5", prompt=False).stdout("Equal", regex=False).exit(0)

@check50.check(test_compile)
def test_extra1():
    """handles input: -5 5"""
    check50.run("./string-compare").stdin("-5 5", prompt=False).stdout("Less", regex=False).exit(0)

@check50.check(test_compile)
def test_extra2():
    """handles input: -10 -20"""
    check50.run("./string-compare").stdin("-10 -20", prompt=False).stdout("Greater", regex=False).exit(0)

@check50.check(test_compile)
def test_extra3():
    """handles input: 100 50"""
    check50.run("./string-compare").stdin("100 50", prompt=False).stdout("Greater", regex=False).exit(0)

@check50.check(test_compile)
def test_extra4():
    """handles input: 0 0"""
    check50.run("./string-compare").stdin("0 0", prompt=False).stdout("Equal", regex=False).exit(0)

@check50.check(test_compile)
def test_extra5():
    """handles input: 1 5"""
    check50.run("./string-compare").stdin("1 5", prompt=False).stdout("Less", regex=False).exit(0)

@check50.check(test_compile)
def test_large_positive():
    """handles positive boundary values: 1000 999"""
    check50.run("./string-compare").stdin("1000 999", prompt=False).stdout("Greater", regex=False).exit(0)

@check50.check(test_compile)
def test_large_negative():
    """handles negative boundary values: -1000 -999"""
    check50.run("./string-compare").stdin("-1000 -999", prompt=False).stdout("Less", regex=False).exit(0)



@check50.check(test_compile)
def test_random():
    """compares random integers correctly"""
    a = random.randint(-1000000, 1000000)
    b = random.randint(-1000000, 1000000)
    expected = "Greater" if a > b else ("Less" if a < b else "Equal")
    check50.run("./string-compare").stdin(f"{a} {b}", prompt=False).stdout(expected, regex=False).exit(0)
