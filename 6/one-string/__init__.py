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
    """one-string.cpp exists"""
    check50.exists("one-string.cpp")

@check50.check(exists)
def test_compile():
    """one-string.cpp compiles successfully"""
    check50.run("g++ -O2 -Wall -Werror one-string.cpp -o one-string").exit(0)

@check50.check(test_compile)
def test_example1():
    """concatenates string and sheet -> stringsheet"""
    check50.run("./one-string").stdin("string\nsheet", prompt=False).stdout("stringsheet", regex=False).exit(0)

@check50.check(test_compile)
def test_extra1():
    """concatenates a and b -> ab"""
    check50.run("./one-string").stdin("a\nb", prompt=False).stdout("ab", regex=False).exit(0)

@check50.check(test_compile)
def test_extra2():
    """concatenates hello and world -> helloworld"""
    check50.run("./one-string").stdin("hello\nworld", prompt=False).stdout("helloworld", regex=False).exit(0)

@check50.check(test_compile)
def test_identical():
    """concatenates identical strings -> samesame"""
    check50.run("./one-string").stdin("same\nsame", prompt=False).stdout("samesame", regex=False).exit(0)

@check50.check(test_compile)
def test_large():
    """concatenates two large strings of length 500 each"""
    check50.run("./one-string").stdin("x" * 500 + "\n" + "y" * 500, prompt=False).stdout("x" * 500 + "y" * 500, regex=False).exit(0)

