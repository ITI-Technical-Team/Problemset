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
    """linear-search.cpp exists"""
    check50.exists("linear-search.cpp")

@check50.check(exists)
def test_compile():
    """linear-search.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG linear-search.cpp -o linear-search", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_example1():
    """finds element in array"""
    check50.run("./linear-search").stdin("3\n3 0 1\n0", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test_example2():
    """checks behavior if target missing"""
    check50.run("./linear-search").stdin("5\n1 3 0 4 5\n10", prompt=False).stdout("-1", regex=False).exit(0)

@check50.check(test_compile)
def test_example3():
    """returns first position for duplicates"""
    check50.run("./linear-search").stdin("4\n2 3 2 1\n2", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_first_element():
    """finds target at index 0"""
    check50.run("./linear-search").stdin("5\n7 1 2 3 4\n7", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_last_element():
    """finds target at last index"""
    check50.run("./linear-search").stdin("5\n1 2 3 4 9\n9", prompt=False).stdout("4", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1_match():
    """handles minimal size N = 1 with a match"""
    check50.run("./linear-search").stdin("1\n99\n99", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1_mismatch():
    """handles minimal size N = 1 with no match"""
    check50.run("./linear-search").stdin("1\n99\n10", prompt=False).stdout("-1", regex=False).exit(0)


@check50.check(test_compile)
def test_random():
    """finds index of target using linear search correctly"""
    n = random.randint(10, 50)
    arr = [random.randint(-1000, 1000) for _ in range(n)]
    if random.choice([True, False]):
        target = random.choice(arr)
        expected = str(arr.index(target))
    else:
        target = 9999
        expected = "-1"
    stdin_data = f"{n}\n" + " ".join(map(str, arr)) + f"\n{target}"
    check50.run("./linear-search").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)
