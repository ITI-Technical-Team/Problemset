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
            expected_str = str(output).strip()
            out = super().stdout(output=None).strip()
            if out.split() != expected_str.split():
                raise check50.Mismatch(expected_str, out)
            return self
        return super().stdout(output, *args, **kwargs)

check50.run = RobustRun

@check50.check()
def exists():
    """pyramid.cpp exists"""
    check50.exists("pyramid.cpp")

@check50.check(exists)
def test_compile():
    """pyramid.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG pyramid.cpp -o pyramid", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_four():
    """handles input: 4"""
    expected = "\n".join("#" * i for i in range(1, 5))
    check50.run("./pyramid").stdin("4", prompt=False).stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_three():
    """handles input: 3"""
    expected = "\n".join("#" * i for i in range(1, 4))
    check50.run("./pyramid").stdin("3", prompt=False).stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random inputs correctly"""
    n = random.randint(1, 20)
    expected = "\n".join("#" * i for i in range(1, n+1))
    check50.run("./pyramid").stdin(str(n), prompt=False).stdout(expected, regex=False).exit(0)
