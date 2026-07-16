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
    """string-compare.cpp exists"""
    check50.exists("string-compare.cpp")

@check50.check(exists)
def test_compile():
    """string-compare.cpp compiles successfully"""
    check50.run("g++ string-compare.cpp -o string-compare").exit(0)

@check50.check(test_compile)
def test_example1():
    """5 1 -> Greater"""
    check50.run("./string-compare").stdin("5 1", prompt=False).stdout("Greater", regex=False).exit(0)

@check50.check(test_compile)
def test_example2():
    """5 5 -> Equal"""
    check50.run("./string-compare").stdin("5 5", prompt=False).stdout("Equal", regex=False).exit(0)

@check50.check(test_compile)
def test_extra1():
    """-5 5 -> Less"""
    check50.run("./string-compare").stdin("-5 5", prompt=False).stdout("Less", regex=False).exit(0)

@check50.check(test_compile)
def test_extra2():
    """-10 -20 -> Greater"""
    check50.run("./string-compare").stdin("-10 -20", prompt=False).stdout("Greater", regex=False).exit(0)

@check50.check(test_compile)
def test_extra3():
    """100 50 -> Greater"""
    check50.run("./string-compare").stdin("100 50", prompt=False).stdout("Greater", regex=False).exit(0)

@check50.check(test_compile)
def test_extra4():
    """0 0 -> Equal"""
    check50.run("./string-compare").stdin("0 0", prompt=False).stdout("Equal", regex=False).exit(0)

@check50.check(test_compile)
def test_extra5():
    """1 5 -> Less"""
    check50.run("./string-compare").stdin("1 5", prompt=False).stdout("Less", regex=False).exit(0)

@check50.check(test_compile)
def test_large_positive():
    """handles positive boundary values: 1000 999 -> Greater"""
    check50.run("./string-compare").stdin("1000 999", prompt=False).stdout("Greater", regex=False).exit(0)

@check50.check(test_compile)
def test_large_negative():
    """handles negative boundary values: -1000 -999 -> Less"""
    check50.run("./string-compare").stdin("-1000 -999", prompt=False).stdout("Less", regex=False).exit(0)


