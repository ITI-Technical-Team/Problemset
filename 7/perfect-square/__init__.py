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
    """perfect-square.cpp exists"""
    check50.exists("perfect-square.cpp")

@check50.check(exists)
def test_compile():
    """perfect-square.cpp compiles successfully"""
    check50.run("g++ perfect-square.cpp -o perfect-square").exit(0)

@check50.check(test_compile)
def test_example1():
    """outputs YES for 25"""
    check50.run("./perfect-square").stdin("25", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_example2():
    """outputs NO for 10"""
    check50.run("./perfect-square").stdin("10", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_one():
    """outputs YES for 1"""
    check50.run("./perfect-square").stdin("1", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_two():
    """outputs NO for 2"""
    check50.run("./perfect-square").stdin("2", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_large_square():
    """outputs YES for 999950884 (31622^2)"""
    check50.run("./perfect-square").stdin("999950884", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_large_non_square():
    """outputs NO for 999950885"""
    check50.run("./perfect-square").stdin("999950885", prompt=False).stdout("NO", regex=False).exit(0)


