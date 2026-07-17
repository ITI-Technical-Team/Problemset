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
    """replacement.cpp exists"""
    check50.exists("replacement.cpp")

@check50.check(exists)
def test_compile():
    """replacement.cpp compiles successfully"""
    check50.run("g++ replacement.cpp -fsanitize=bounds -fno-sanitize-recover=bounds -o replacement").exit(0)

@check50.check(test_compile)
def test1():
    """swaps elements correctly (Example 1)"""
    check50.run("./replacement").stdin("5 2 4\n1 2 3 4 5", prompt=False).stdout("1 4 3 2 5", regex=False).exit(0)

@check50.check(test_compile)
def test2():
    """swaps elements correctly (Example 2)"""
    check50.run("./replacement").stdin("4 1 4\n5 3 2 6", prompt=False).stdout("6 3 2 5", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles edge case N = 1"""
    check50.run("./replacement").stdin("1 1 1\n999", prompt=False).stdout("999", regex=False).exit(0)

@check50.check(test_compile)
def test_identity_swap():
    """handles swapping an element with itself (a = b)"""
    check50.run("./replacement").stdin("5 3 3\n1 2 3 4 5", prompt=False).stdout("1 2 3 4 5", regex=False).exit(0)

@check50.check(test_compile)
def test_endpoint_swap():
    """handles swapping first and last elements (a = 1, b = n)"""
    check50.run("./replacement").stdin("5 1 5\n10 20 30 40 50", prompt=False).stdout("50 20 30 40 10", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1000():
    """handles N = 1000 with swapping the endpoints"""
    stdin_data = "1000 1 1000\n" + " ".join(str(i) for i in range(1, 1001))
    expected_out = "1000 " + " ".join(str(i) for i in range(2, 1000)) + " 1"
    check50.run("./replacement").stdin(stdin_data, prompt=False).stdout(expected_out, regex=False).exit(0)


@check50.check(test_compile)
def test_random():
    """swaps random elements in a random array correctly"""
    n = random.randint(10, 50)
    a = random.randint(1, n)
    b = random.randint(1, n)
    arr = [random.randint(-1000, 1000) for _ in range(n)]
    expected_arr = list(arr)
    expected_arr[a-1], expected_arr[b-1] = expected_arr[b-1], expected_arr[a-1]
    expected = " ".join(map(str, expected_arr))
    stdin_data = f"{n} {a} {b}\n" + " ".join(map(str, arr))
    check50.run("./replacement").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)
