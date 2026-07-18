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
	"""absolute.cpp exists"""
	check50.exists("absolute.cpp")

@check50.check(exists)
def test_no_abs():
	"""solution does not use the abs() function"""
	with open("absolute.cpp") as f:
		source = f.read()
	if "abs(" in source:
		raise check50.Failure("Do not use abs() — compute the absolute value manually")

@check50.check(test_no_abs)
def test_compile():
	"""absolute.cpp compiles successfully"""
	import subprocess as _sp
	_res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG absolute.cpp -o absolute", shell=True, capture_output=True, text=True)
	if _res.returncode != 0:
	    raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test1():
	"""handles input: 4 7"""
	check50.run("./absolute").stdin("4 7", prompt=False).stdout("3", regex=False).exit(0)

@check50.check(test_compile)
def test2():
	"""handles input: 9 2"""
	check50.run("./absolute").stdin("9 2", prompt=False).stdout("7", regex=False).exit(0)

@check50.check(test_compile)
def test3():
	"""handles input: 5 5"""
	check50.run("./absolute").stdin("5 5", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test4():
	"""handles input: 1000000 999999"""
	check50.run("./absolute").stdin("1000000 999999", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test5():
	"""handles input: 1000000 1000000"""
	check50.run("./absolute").stdin("1000000 1000000", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
	"""handles random inputs correctly"""
	a = random.randint(-1000000, 1000000)
	b = random.randint(-1000000, 1000000)
	expected = str(abs(a - b))
	check50.run("./absolute").stdin(f"{a} {b}", prompt=False).stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_random2():
	"""handles a second set of random inputs correctly"""
	a = random.randint(-1000000, 1000000)
	b = random.randint(-1000000, 1000000)
	expected = str(abs(a - b))
	check50.run("./absolute").stdin(f"{a} {b}", prompt=False).stdout(expected, regex=False).exit(0)
