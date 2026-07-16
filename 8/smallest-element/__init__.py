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
    """smallest-element.cpp exists"""
    check50.exists("smallest-element.cpp")

@check50.check(exists)
def test_compile():
    """smallest-element.cpp compiles successfully"""
    check50.run("g++ -O2 -Wall -Werror smallest-element.cpp -o smallest-element").exit(0)

@check50.check(test_compile)
def test_example1():
    """finds k-th smallest element correctly (Example 1)"""
    check50.run("./smallest-element").stdin("5 3\n64 25 12 22 11", prompt=False).stdout("22", regex=False).exit(0)

@check50.check(test_compile)
def test_example2():
    """finds k-th smallest element correctly (Example 2)"""
    check50.run("./smallest-element").stdin("6 4\n30 10 20 50 40 60", prompt=False).stdout("40", regex=False).exit(0)

@check50.check(test_compile)
def test_k1():
    """handles k = 1 (absolute smallest)"""
    check50.run("./smallest-element").stdin("4 1\n8 9 7 6", prompt=False).stdout("6", regex=False).exit(0)

@check50.check(test_compile)
def test_kN():
    """handles k = N (absolute largest)"""
    check50.run("./smallest-element").stdin("4 4\n8 9 7 6", prompt=False).stdout("9", regex=False).exit(0)

@check50.check(test_compile)
def test_mid_with_duplicates():
    """handles mid-k with duplicates"""
    check50.run("./smallest-element").stdin("7 4\n5 1 3 3 2 9 5", prompt=False).stdout("3", regex=False).exit(0)
