import check50

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
    """a-to-e.cpp exists"""
    check50.exists("a-to-e.cpp")

@check50.check(exists)
def test_compile():
    """a-to-e.cpp compiles successfully"""
    check50.run("g++ -O2 -Wall -Werror a-to-e.cpp -o a-to-e").exit(0)

@check50.check(test_compile)
def test_example1():
    """handles input: 3 ace -> YES"""
    check50.run("./a-to-e").stdin("3\nace", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_extra1():
    """handles input with f: 4 abcf -> NO"""
    check50.run("./a-to-e").stdin("4\nabcf", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_extra2():
    """handles all valid chars: 5 abcde -> YES"""
    check50.run("./a-to-e").stdin("5\nabcde", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_extra3():
    """handles z: 1 z -> NO"""
    check50.run("./a-to-e").stdin("1\nz", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_minimal_yes():
    """handles minimal YES: 1 a -> YES"""
    check50.run("./a-to-e").stdin("1\na", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_minimal_no():
    """handles minimal NO: 1 f -> NO"""
    check50.run("./a-to-e").stdin("1\nf", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_large_yes():
    """handles large valid string N = 1000"""
    check50.run("./a-to-e").stdin("1000\n" + "e" * 1000, prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_large_no():
    """handles large string N = 1000 with invalid character at the end"""
    check50.run("./a-to-e").stdin("1000\n" + "e" * 999 + "f", prompt=False).stdout("NO", regex=False).exit(0)

