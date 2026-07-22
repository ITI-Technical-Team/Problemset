import check50
import random
import re

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
            expected_str = str(output).strip()
            out = super().stdout(output=None).strip()
            if out.split() != expected_str.split():
                raise check50.Mismatch(expected_str, out)
            return self
        return super().stdout(output, *args, **kwargs)

check50.run = RobustRun

@check50.check()
def exists():
    """vector-remove-even.cpp exists"""
    check50.exists("vector-remove-even.cpp")

@check50.check(exists)
def test_compile():
    """vector-remove-even.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG vector-remove-even.cpp -o vector-remove-even", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_example():
    """removes even numbers from the example vector {1, 2, 3, 4, 5, 6}"""
    check50.run("./vector-remove-even").stdin("6\n1 2 3 4 5 6", prompt=False).stdout("1 3 5", regex=False).exit(0)

@check50.check(test_compile)
def test_all_even():
    """handles vector with all even numbers"""
    check50.run("./vector-remove-even").stdin("4\n2 4 6 8", prompt=False).stdout("", regex=False).exit(0)

@check50.check(test_compile)
def test_all_odd():
    """handles vector with all odd numbers"""
    check50.run("./vector-remove-even").stdin("4\n1 3 5 7", prompt=False).stdout("1 3 5 7", regex=False).exit(0)

@check50.check(test_compile)
def test_negative_values():
    """handles negative values in vector"""
    check50.run("./vector-remove-even").stdin("5\n-1 -2 -3 -4 5", prompt=False).stdout("-1 -3 5", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """removes even numbers in random vector correctly"""
    n = random.randint(10, 40)
    arr = [random.randint(-100, 100) for _ in range(n)]
    expected = " ".join(map(str, [x for x in arr if x % 2 != 0]))
    stdin_data = f"{n}\n" + " ".join(map(str, arr))
    check50.run("./vector-remove-even").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_vector_used():
    """vector container is used in vector-remove-even.cpp"""
    with open("vector-remove-even.cpp", "r") as f:
        code = f.read()
    
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    if "vector" not in code_clean:
        raise check50.Failure("std::vector is not used in vector-remove-even.cpp.")
