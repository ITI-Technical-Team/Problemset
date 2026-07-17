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
    """summation.cpp exists"""
    check50.exists("summation.cpp")

@check50.check(exists)
def test_compile():
    """summation.cpp compiles successfully"""
    check50.run("g++ -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG summation.cpp -o summation").exit(0)

@check50.check(test_compile)
def sums_5_numbers():
    """sums five numbers (Example 1)"""
    check50.run("./summation").stdin("5\n2 4 3 1 5", prompt=False).stdout("15", regex=False).exit(0)

@check50.check(test_compile)
def sums_7_numbers():
    """sums seven numbers (Example 2)"""
    check50.run("./summation").stdin("7\n1 5 2 10 -4 -3 6", prompt=False).stdout("17", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles edge case N = 1 (minimal size)"""
    check50.run("./summation").stdin("1\n42", prompt=False).stdout("42", regex=False).exit(0)

@check50.check(test_compile)
def test_negative_sums():
    """handles negative integers correctly"""
    check50.run("./summation").stdin("3\n-5 -10 -2", prompt=False).stdout("-17", regex=False).exit(0)

@check50.check(test_compile)
def test_all_zeroes():
    """handles all zeroes correctly"""
    check50.run("./summation").stdin("4\n0 0 0 0", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_n_100_maximal():
    """handles edge case N = 100 with large mixed values"""
    elements = " ".join(["100"] * 100)
    check50.run("./summation").stdin(f"100\n{elements}", prompt=False).stdout("10000", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """sums a random sequence of numbers correctly"""
    n = random.randint(15, 50)
    numbers = [random.randint(-1000, 1000) for _ in range(n)]
    expected = str(sum(numbers))
    stdin_input = f"{n}\n" + " ".join(map(str, numbers))
    check50.run("./summation").stdin(stdin_input, prompt=False).stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """sums a random sequence of numbers correctly"""
    n = random.randint(15, 50)
    numbers = [random.randint(-1000, 1000) for _ in range(n)]
    expected = str(sum(numbers))
    stdin_input = f"{n}\n" + " ".join(map(str, numbers))
    check50.run("./summation").stdin(stdin_input, prompt=False).stdout(expected, regex=False).exit(0)
