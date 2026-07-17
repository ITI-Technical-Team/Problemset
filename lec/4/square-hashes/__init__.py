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
    """square-hashes.cpp exists"""
    check50.exists("square-hashes.cpp")

@check50.check(exists)
def test_compile():
    """square-hashes.cpp compiles successfully"""
    check50.run("g++ square-hashes.cpp -o square-hashes").exit(0)

@check50.check(test_compile)
def test_four():
    """handles input: 4"""
    expected = "\n".join("####" for _ in range(4))
    check50.run("./square-hashes").stdin("4", prompt=False).stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_three():
    """handles input: 3"""
    expected = "\n".join("###" for _ in range(3))
    check50.run("./square-hashes").stdin("3", prompt=False).stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random inputs correctly"""
    n = random.randint(1, 15)
    row = "#" * n
    expected = "\n".join(row for _ in range(n))
    check50.run("./square-hashes").stdin(str(n), prompt=False).stdout(expected, regex=False).exit(0)
