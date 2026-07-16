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
    """hashes.cpp exists"""
    check50.exists("hashes.cpp")

@check50.check(exists)
def test_compile():
    """hashes.cpp compiles successfully"""
    check50.run("g++ hashes.cpp -o hashes").exit(0)

@check50.check(test_compile)
def prints_3_hashes():
    """prints three hashes (Example 1)"""
    check50.run("./hashes").stdin("3", prompt=False).stdout("###", regex=False).exit(0)

@check50.check(test_compile)
def prints_5_hashes():
    """prints five hashes (Example 2)"""
    check50.run("./hashes").stdin("5", prompt=False).stdout("#####", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles edge case N = 1 (minimal value)"""
    check50.run("./hashes").stdin("1", prompt=False).stdout("#", regex=False).exit(0)

@check50.check(test_compile)
def test_n_100():
    """handles edge case N = 100 (maximal value)"""
    check50.run("./hashes").stdin("100", prompt=False).stdout("#" * 100, regex=False).exit(0)
