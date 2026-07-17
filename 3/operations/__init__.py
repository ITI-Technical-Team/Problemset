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
	"""operations.cpp exists"""
	check50.exists("operations.cpp")

@check50.check(exists)
def test_compile():
	"""operations.cpp compiles successfully"""
	check50.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG operations.cpp -o operations").exit(0)

@check50.check(test_compile)
def test1():
	"""handles input: 5 3"""
	check50.run("./operations").stdin("5 3", prompt=False).stdout("8\n2\n15\n1", regex=False).exit(0)

@check50.check(test_compile)
def test2():
	"""handles input: 10 4"""
	check50.run("./operations").stdin("10 4", prompt=False).stdout("14\n6\n40\n2", regex=False).exit(0)

@check50.check(test_compile)
def test3():
	"""handles input: 1 1"""
	check50.run("./operations").stdin("1 1", prompt=False).stdout("2\n0\n1\n1", regex=False).exit(0)

@check50.check(test_compile)
def test4():
	"""handles input: 5 5"""
	check50.run("./operations").stdin("5 5", prompt=False).stdout("10\n0\n25\n1", regex=False).exit(0)

@check50.check(test_compile)
def test5():
	"""handles input: 100000000 100000000"""
	check50.run("./operations").stdin("100000000 100000000", prompt=False).stdout("200000000\n0\n10000000000000000\n1", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random calculations correctly"""
    a = random.randint(-10000, 10000)
    b = random.choice([x for x in range(-10000, 10000) if x != 0])
    expected = f"{a + b}\n{a - b}\n{a * b}\n{int(a / b)}"
    check50.run("./operations").stdin(f"{a} {b}", prompt=False).stdout(expected, regex=False).exit(0)
