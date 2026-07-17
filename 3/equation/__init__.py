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
	"""equation.cpp exists"""
	check50.exists("equation.cpp")

@check50.check(exists)
def test_compile():
	"""equation.cpp compiles successfully"""
	check50.run("g++ -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG equation.cpp -o equation").exit(0)

@check50.check(test_compile)
def test1():
	"""handles input: 4 2 5 3"""
	check50.run("./equation").stdin("4 2 5 3", prompt=False).stdout("10", regex=False).exit(0)

@check50.check(test_compile)
def test2():
	"""handles input: 1 1 1 1"""
	check50.run("./equation").stdin("1 1 1 1", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test3():
	"""handles input: 2 2 2 2"""
	check50.run("./equation").stdin("2 2 2 2", prompt=False).stdout("4", regex=False).exit(0)

@check50.check(test_compile)
def test4():
	"""handles input: 10 5 2 1"""
	check50.run("./equation").stdin("10 5 2 1", prompt=False).stdout("51", regex=False).exit(0)

@check50.check(test_compile)
def test5():
	"""handles input: 3 2 1 1"""
	check50.run("./equation").stdin("3 2 1 1", prompt=False).stdout("6", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random inputs correctly"""
    a = random.randint(-1000, 1000)
    b = random.randint(-1000, 1000)
    c = random.randint(-1000, 1000)
    d = random.randint(-1000, 1000)
    expected = str((a * b) + (c - d))
    check50.run("./equation").stdin(f"{a} {b} {c} {d}", prompt=False).stdout(expected, regex=False).exit(0)
