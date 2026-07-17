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
    """second-maximum.cpp exists"""
    check50.exists("second-maximum.cpp")

@check50.check(exists)
def test_compile():
    """second-maximum.cpp compiles successfully"""
    check50.run("g++ -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG second-maximum.cpp -o second-maximum").exit(0)

@check50.check(test_compile)
def test_example1():
    """finds second maximum correctly (Example 1)"""
    check50.run("./second-maximum").stdin("5\n9 5 10 1 3", prompt=False).stdout("9", regex=False).exit(0)

@check50.check(test_compile)
def test_example2():
    """finds second maximum correctly (Example 2)"""
    check50.run("./second-maximum").stdin("6\n1 8 4 9 2 3", prompt=False).stdout("8", regex=False).exit(0)

@check50.check(test_compile)
def test_minimal():
    """handles minimal array size N = 2 with distinct values"""
    check50.run("./second-maximum").stdin("2\n5 10", prompt=False).stdout("5", regex=False).exit(0)

@check50.check(test_compile)
def test_large_values():
    """handles large values near 10^5"""
    check50.run("./second-maximum").stdin("4\n99999 100000 99998 5", prompt=False).stdout("99999", regex=False).exit(0)

@check50.check(test_compile)
def test_sorted():
    """handles already sorted distinct array"""
    check50.run("./second-maximum").stdin("5\n2 4 6 8 10", prompt=False).stdout("8", regex=False).exit(0)

@check50.check(test_compile)
def test_reverse_sorted():
    """handles reverse sorted distinct array"""
    check50.run("./second-maximum").stdin("5\n10 8 6 4 2", prompt=False).stdout("8", regex=False).exit(0)


@check50.check(test_compile)
def test_second_maximum_after_maximum():
    """handles second maximum occurring after the maximum"""
    check50.run("./second-maximum").stdin("3\n10 5 8", prompt=False).stdout("8", regex=False).exit(0)


@check50.check(test_compile)
def test_random():
    """finds second maximum correctly on random distinct arrays"""
    for _ in range(10):
        n = random.randint(10, 50)
        arr = random.sample(range(-1000, 1000), n)
        expected = str(sorted(arr)[-2])
        stdin_data = f"{n}\n" + " ".join(map(str, arr))
        check50.run("./second-maximum").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)
