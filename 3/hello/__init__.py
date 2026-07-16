import check50
import string
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
	"""hello.cpp exists"""
	check50.exists("hello.cpp")

@check50.check(exists)
def test_compile():
	"""hello.cpp compiles successfully"""
	check50.run("g++ hello.cpp -o hello").exit(0)

@check50.check(test_compile)
def test1():
	"""Mohamed 24 -> Hello Mohamed, you are 24 years old."""
	check50.run("./hello").stdin("Mohamed 24", prompt=False).stdout("Hello Mohamed, you are 24 years old.", regex=False).exit(0)

@check50.check(test_compile)
def test2():
	"""Mazen 50 -> Hello Mazen, you are 50 years old."""
	check50.run("./hello").stdin("Mazen 50", prompt=False).stdout("Hello Mazen, you are 50 years old.", regex=False).exit(0)

@check50.check(test_compile)
def test3():
	"""John 30 -> Hello John, you are 30 years old."""
	check50.run("./hello").stdin("John 30", prompt=False).stdout("Hello John, you are 30 years old.", regex=False).exit(0)

@check50.check(test_compile)
def test4():
	"""Alice 22 -> Hello Alice, you are 22 years old."""
	check50.run("./hello").stdin("Alice 22", prompt=False).stdout("Hello Alice, you are 22 years old.", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random name and age correctly"""
    name = "".join(random.choices(string.ascii_letters, k=8))
    age = random.randint(1, 100)
    expected = f"Hello {name}, you are {age} years old."
    check50.run("./hello").stdin(f"{name} {age}", prompt=False).stdout(expected, regex=False).exit(0)
