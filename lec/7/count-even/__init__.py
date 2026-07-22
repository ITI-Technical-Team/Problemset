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
    """count-even.cpp exists"""
    check50.exists("count-even.cpp")

@check50.check(exists)
def test_compile():
    """count-even.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG count-even.cpp -o count-even", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_example():
    """counts even numbers in the example array {1, 7, 7, 15, 10}"""
    check50.run("./count-even").stdin("5\n1 7 7 15 10", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test_all_even():
    """handles array of all even numbers"""
    check50.run("./count-even").stdin("4\n2 4 6 8", prompt=False).stdout("4", regex=False).exit(0)

@check50.check(test_compile)
def test_all_odd():
    """handles array of all odd numbers"""
    check50.run("./count-even").stdin("4\n1 3 5 7", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_negative_even():
    """handles negative even numbers"""
    check50.run("./count-even").stdin("5\n-2 -4 -5 0 3", prompt=False).stdout("3", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles array of size 1"""
    check50.run("./count-even").stdin("1\n0", prompt=False).stdout("1", regex=False).exit(0)
    check50.run("./count-even").stdin("1\n3", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """counts even numbers in a random array correctly"""
    n = random.randint(10, 50)
    arr = [random.randint(-1000, 1000) for _ in range(n)]
    expected = str(sum(1 for x in arr if x % 2 == 0))
    stdin_data = f"{n}\n" + " ".join(map(str, arr))
    check50.run("./count-even").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_function_defined():
    """countEvenNumbers function is defined in count-even.cpp"""
    with open("count-even.cpp", "r") as f:
        code = f.read()
    
    # Remove comments
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    # Search for countEvenNumbers signature
    if not re.search(r'\bint\s+countEvenNumbers\s*\([^)]*\)', code_clean):
        raise check50.Failure(
            "Could not find function 'int countEvenNumbers(int arr[], int size)' defined.",
            help="Define the function with the signature: int countEvenNumbers(int arr[], int size) as shown in the slide."
        )
