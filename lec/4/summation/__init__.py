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
    """summation.cpp exists"""
    check50.exists("summation.cpp")

@check50.check(exists)
def test_compile():
    """summation.cpp compiles successfully"""
    check50.run("g++ -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG summation.cpp -o summation").exit(0)

@check50.check(test_compile)
def test_five():
    """handles input: 5 and numbers: 2 4 3 2 1"""
    run = check50.run("./summation").stdin("5", prompt=False)
    for x in ["2", "4", "3", "2", "1"]:
        run.stdin(x, prompt=False)
    run.stdout("12", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random inputs correctly"""
    n = random.randint(1, 20)
    nums = [random.randint(-100, 100) for _ in range(n)]
    total = sum(nums)
    run = check50.run("./summation").stdin(str(n), prompt=False)
    for x in nums:
        run.stdin(str(x), prompt=False)
    run.stdout(str(total), regex=False).exit(0)
