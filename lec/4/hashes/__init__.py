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
            if out != expected_str:
                raise check50.Mismatch(expected_str, out)
            return self
        return super().stdout(output, *args, **kwargs)

check50.run = RobustRun

@check50.check()
def exists():
    """hashes.cpp exists"""
    check50.exists("hashes.cpp")

@check50.check(exists)
def test_compile():
    """hashes.cpp compiles successfully"""
    check50.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG hashes.cpp -o hashes 2>&1").exit(0)

@check50.check(test_compile)
def test_five():
    """handles input: 5"""
    check50.run("./hashes").stdin("5", prompt=False).stdout("#####", regex=False).exit(0)

@check50.check(test_compile)
def test_ten():
    """handles input: 10"""
    check50.run("./hashes").stdin("10", prompt=False).stdout("##########", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random inputs correctly"""
    n = random.randint(1, 100)
    expected = "#" * n
    check50.run("./hashes").stdin(str(n), prompt=False).stdout(expected, regex=False).exit(0)
