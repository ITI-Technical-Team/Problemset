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
    """guess-number.cpp exists"""
    check50.exists("guess-number.cpp")

@check50.check(exists)
def test_compile():
    """guess-number.cpp compiles successfully"""
    check50.run("g++ -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG guess-number.cpp -o guess-number").exit(0)

@check50.check(test_compile)
def test_case1():
    """handles input: P and 5 (positive)"""
    check50.run("./guess-number").stdin("P", prompt=False).stdin("5", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_case2():
    """handles input: N and -1 (negative)"""
    check50.run("./guess-number").stdin("N", prompt=False).stdin("-1", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_case3():
    """handles input: P and -5 (incorrect guess)"""
    check50.run("./guess-number").stdin("P", prompt=False).stdin("-5", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_case4():
    """handles input: Z and 0 (zero)"""
    check50.run("./guess-number").stdin("Z", prompt=False).stdin("0", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_case5():
    """handles input: Z and 12 (incorrect guess)"""
    check50.run("./guess-number").stdin("Z", prompt=False).stdin("12", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random inputs correctly"""
    guess = random.choice(["P", "N", "Z"])
    num = random.randint(-100, 100)
    
    # Calculate correctness
    is_correct = False
    if guess == "P" and num > 0:
        is_correct = True
    elif guess == "N" and num < 0:
        is_correct = True
    elif guess == "Z" and num == 0:
        is_correct = True
        
    expected = "YES" if is_correct else "NO"
    check50.run("./guess-number").stdin(guess, prompt=False).stdin(str(num), prompt=False).stdout(expected, regex=False).exit(0)
