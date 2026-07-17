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
    """maximum.cpp exists"""
    check50.exists("maximum.cpp")

@check50.check(exists)
def test_compile():
    """maximum.cpp compiles successfully"""
    check50.run("g++ maximum.cpp -fsanitize=bounds -fno-sanitize-recover=bounds -o maximum").exit(0)

@check50.check(test_compile)
def test_example1():
    """counts divisors of max correctly (Example 1)"""
    check50.run("./maximum").stdin("7\n3 2 4 1 10 6 8", prompt=False).stdout("3", regex=False).exit(0)

@check50.check(test_compile)
def test_example2():
    """counts divisors of max correctly (Example 2)"""
    check50.run("./maximum").stdin("3\n2 4 11", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test_all_equal():
    """handles arrays where all elements equal the max"""
    check50.run("./maximum").stdin("4\n5 5 5 5", prompt=False).stdout("4", regex=False).exit(0)

@check50.check(test_compile)
def test_mixed_divisors():
    """handles a mixed array with several divisors"""
    # max = 12. Divisors: 6, 3, 2, 1, 12 (5 elements)
    check50.run("./maximum").stdin("6\n6 3 2 1 12 7", prompt=False).stdout("5", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles minimal array size N = 1"""
    check50.run("./maximum").stdin("1\n999", prompt=False).stdout("1", regex=False).exit(0)


@check50.check(test_compile)
def test_random():
    """counts divisors of max in a random array correctly"""
    n = random.randint(10, 50)
    arr = [random.randint(1, 1000) for _ in range(n)]
    mx = max(arr)
    expected = str(sum(1 for x in arr if mx % x == 0))
    stdin_data = f"{n}\n" + " ".join(map(str, arr))
    check50.run("./maximum").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)
