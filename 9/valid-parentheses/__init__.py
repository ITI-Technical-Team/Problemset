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
    """valid-parentheses.cpp exists"""
    check50.exists("valid-parentheses.cpp")

@check50.check(exists)
def test_compile():
    """valid-parentheses.cpp compiles successfully"""
    check50.run("g++ -O2 -Wall -Werror valid-parentheses.cpp -o valid-parentheses").exit(0)

@check50.check(test_compile)
def test_examples_set1():
    """validates multiple sequences (Example set 1)"""
    check50.run("./valid-parentheses").stdin("3\n()\n((\n())(", prompt=False).stdout("YES\nNO\nNO", regex=False).exit(0)

@check50.check(test_compile)
def test_examples_set2():
    """validates multiple sequences (Example set 2)"""
    check50.run("./valid-parentheses").stdin("4\n)()(())\n()(((()\n(((())))\n(())(())", prompt=False).stdout("NO\nNO\nYES\nYES", regex=False).exit(0)

@check50.check(test_compile)
def test_mixed_cases():
    """handles mixed valid and invalid cases"""
    check50.run("./valid-parentheses").stdin("5\n()\n)(\n((()))\n(()))(\n()(())", prompt=False).stdout("YES\nNO\nYES\nNO\nYES", regex=False).exit(0)

@check50.check(test_compile)
def test_longer():
    """handles longer sequences"""
    check50.run("./valid-parentheses").stdin("2\n((((()))))(()())\n())(()", prompt=False).stdout("YES\nNO", regex=False).exit(0)

@check50.check(test_compile)
def test_minimal_size():
    """handles minimal parenthesized strings of length 1"""
    check50.run("./valid-parentheses").stdin("2\n(\n)", prompt=False).stdout("NO\nNO", regex=False).exit(0)

