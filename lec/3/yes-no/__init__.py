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
    """yes-no.cpp exists"""
    check50.exists("yes-no.cpp")

@check50.check(exists)
def test_compile():
    """yes-no.cpp compiles successfully"""
    check50.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG yes-no.cpp -o yes-no 2>&1").exit(0)

@check50.check(test_compile)
def test_y_upper():
    """handles input: Y"""
    check50.run("./yes-no").stdin("Y", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_y_lower():
    """handles input: y"""
    check50.run("./yes-no").stdin("y", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_n_upper():
    """handles input: N"""
    check50.run("./yes-no").stdin("N", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_n_lower():
    """handles input: n"""
    check50.run("./yes-no").stdin("n", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_invalid():
    """handles input: v (invalid option)"""
    check50.run("./yes-no").stdin("v", prompt=False).stdout("Invalid option!", regex=False).exit(0)

@check50.check(test_compile)
def test_random_invalid():
    """handles other random letters as invalid option"""
    c = random.choice([chr(i) for i in range(65, 123) if chr(i) not in ['y', 'Y', 'n', 'N']])
    check50.run("./yes-no").stdin(c, prompt=False).stdout("Invalid option!", regex=False).exit(0)
