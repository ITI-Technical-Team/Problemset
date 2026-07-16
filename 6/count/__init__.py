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
    """count.cpp exists"""
    check50.exists("count.cpp")

@check50.check(exists)
def test_compile():
    """count.cpp compiles successfully"""
    check50.run("g++ count.cpp -o count").exit(0)

@check50.check(test_compile)
def test_example1():
    """counts 'l' in 'hello' -> 2"""
    check50.run("./count").stdin("hello\nl", prompt=False).stdout("2", regex=False).exit(0)

@check50.check(test_compile)
def test_extra1():
    """counts 'z' in 'hello' -> 0"""
    check50.run("./count").stdin("hello\nz", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_extra2():
    """counts 'a' in 'aaaaa' -> 5"""
    check50.run("./count").stdin("aaaaa\na", prompt=False).stdout("5", regex=False).exit(0)

@check50.check(test_compile)
def test_extra3():
    """counts 'b' in 'abcde' -> 1"""
    check50.run("./count").stdin("abcde\nb", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test_minimal_match():
    """handles minimal string with a match: a, count 'a' -> 1"""
    check50.run("./count").stdin("a\na", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test_minimal_no_match():
    """handles minimal string with no match: a, count 'b' -> 0"""
    check50.run("./count").stdin("a\nb", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_case_sensitivity():
    """handles case sensitivity: A, count 'a' -> 0"""
    check50.run("./count").stdin("A\na", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_large_count():
    """handles large string N = 1000 all matching"""
    check50.run("./count").stdin("x" * 1000 + "\nx", prompt=False).stdout("1000", regex=False).exit(0)


@check50.check(test_compile)
def test_random():
    """counts target char in a random string correctly"""
    s = "".join(random.choices(string.ascii_letters, k=50))
    c = random.choice(string.ascii_letters)
    expected = str(s.count(c))
    check50.run("./count").stdin(f"{s}\n{c}", prompt=False).stdout(expected, regex=False).exit(0)
