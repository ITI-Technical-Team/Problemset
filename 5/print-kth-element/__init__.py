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
    """print-kth-element.cpp exists"""
    check50.exists("print-kth-element.cpp")

@check50.check(exists)
def test_compile():
    """print-kth-element.cpp compiles successfully"""
    check50.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG print-kth-element.cpp -o print-kth-element").exit(0)

@check50.check(test_compile)
def test1():
    """finds 2nd element in 6 elements"""
    check50.run("./print-kth-element").stdin("6 2\n1 2 3 4 5 6", prompt=False).stdout("2", regex=False).exit(0)

@check50.check(test_compile)
def test2():
    """finds 1st element in 3 elements"""
    check50.run("./print-kth-element").stdin("3 1\n5 22 1", prompt=False).stdout("5", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles edge case N = 1, K = 1 (minimal value)"""
    check50.run("./print-kth-element").stdin("1 1\n999", prompt=False).stdout("999", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1000():
    """handles edge case N = 1000, K = 1000 (large value)"""
    stdin_data = "1000 1000\n" + " ".join(str(i) for i in range(1, 1001))
    check50.run("./print-kth-element").stdin(stdin_data, prompt=False).stdout("1000", regex=False).exit(0)


@check50.check(test_compile)
def test_random():
    """prints kth element of a random array correctly"""
    n = random.randint(10, 50)
    k = random.randint(1, n)
    arr = [random.randint(-1000, 1000) for _ in range(n)]
    expected = str(arr[k-1])
    stdin_data = f"{n} {k}\n" + " ".join(map(str, arr))
    check50.run("./print-kth-element").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)
