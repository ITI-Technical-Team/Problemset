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
    """numbers-1-to-n.cpp exists"""
    check50.exists("numbers-1-to-n.cpp")

@check50.check(exists)
def test_compile():
    """numbers-1-to-n.cpp compiles successfully"""
    check50.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG numbers-1-to-n.cpp -o numbers-1-to-n").exit(0)

@check50.check(test_compile)
def test_five():
    """handles input: 5"""
    check50.run("./numbers-1-to-n").stdin("5", prompt=False).stdout("1 2 3 4 5", regex=False).exit(0)

@check50.check(test_compile)
def test_ten():
    """handles input: 10"""
    check50.run("./numbers-1-to-n").stdin("10", prompt=False).stdout("1 2 3 4 5 6 7 8 9 10", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random inputs correctly"""
    n = random.randint(1, 50)
    expected = " ".join(str(i) for i in range(1, n+1))
    check50.run("./numbers-1-to-n").stdin(str(n), prompt=False).stdout(expected, regex=False).exit(0)
