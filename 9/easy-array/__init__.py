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
    """easy-array.cpp exists"""
    check50.exists("easy-array.cpp")

@check50.check(exists)
def test_compile():
    """easy-array.cpp compiles successfully"""
    check50.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG easy-array.cpp -o easy-array 2>&1").exit(0)

@check50.check(test_compile)
def test_example():
    """sums 2D array correctly (Example)"""
    check50.run("./easy-array").stdin("3 3\n1 2 3\n4 5 6\n7 8 9", prompt=False).stdout("45", regex=False).exit(0)

@check50.check(test_compile)
def test_small():
    """handles 2x2 array"""
    check50.run("./easy-array").stdin("2 2\n1 1\n1 1", prompt=False).stdout("4", regex=False).exit(0)

@check50.check(test_compile)
def test_rectangular():
    """handles non-square array"""
    check50.run("./easy-array").stdin("2 3\n10 20 30\n40 50 60", prompt=False).stdout("210", regex=False).exit(0)

@check50.check(test_compile)
def test_larger():
    """handles larger values and size"""
    # Sum: 1000 + (1+2+3+4+5+6+7+8+9+10+11+12+13+14+15) = 1000 + 120 = 1120.
    check50.run("./easy-array").stdin("4 4\n1000 1 2 3\n4 5 6 7\n8 9 10 11\n12 13 14 15", prompt=False).stdout("1120", regex=False).exit(0)

@check50.check(test_compile)
def test_minimal():
    """handles minimal elements (all 1s)"""
    check50.run("./easy-array").stdin("2 2\n1 1\n1 1", prompt=False).stdout("4", regex=False).exit(0)

@check50.check(test_compile)
def test_distinct_values():
    """handles distinct positive elements within bounds"""
    check50.run("./easy-array").stdin("2 2\n100 200\n300 400", prompt=False).stdout("1000", regex=False).exit(0)

@check50.check(test_compile)
def test_maximal_bounds():
    """handles maximal bounds (10x10 array of all 1000s)"""
    elements = "\n".join(" ".join(["1000"] * 10) for _ in range(10))
    check50.run("./easy-array").stdin(f"10 10\n{elements}", prompt=False).stdout("100000", regex=False).exit(0)


@check50.check(test_compile)
def test_random():
    """sums random 2D array correctly"""
    r = random.randint(3, 10)
    c = random.randint(3, 10)
    elements = [[random.randint(-1000, 1000) for _ in range(c)] for _ in range(r)]
    expected = str(sum(sum(row) for row in elements))
    stdin_data = f"{r} {c}\n" + "\n".join(" ".join(map(str, row)) for row in elements)
    check50.run("./easy-array").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)
