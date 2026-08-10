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
    """find-minimum.cpp exists"""
    check50.exists("find-minimum.cpp")

@check50.check(exists)
def test_compile():
    """find-minimum.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG find-minimum.cpp -o find-minimum", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_example():
    """finds minimum in the example array {1, 7, 7, 15, 10}"""
    check50.run("./find-minimum").stdin("5\n1 7 7 15 10", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test_minimum_at_end():
    """finds minimum at the end of the array"""
    check50.run("./find-minimum").stdin("4\n10 20 30 5", prompt=False).stdout("5", regex=False).exit(0)

@check50.check(test_compile)
def test_minimum_in_middle():
    """finds minimum in the middle of the array"""
    check50.run("./find-minimum").stdin("5\n15 8 -3 10 12", prompt=False).stdout("-3", regex=False).exit(0)

@check50.check(test_compile)
def test_negative_values():
    """handles array of negative values"""
    check50.run("./find-minimum").stdin("4\n-10 -20 -30 -5", prompt=False).stdout("-30", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles array of size 1"""
    check50.run("./find-minimum").stdin("1\n99", prompt=False).stdout("99", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """finds minimum in a random array correctly"""
    n = random.randint(10, 50)
    arr = [random.randint(-1000, 1000) for _ in range(n)]
    expected = str(min(arr))
    stdin_data = f"{n}\n" + " ".join(map(str, arr))
    check50.run("./find-minimum").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_function_defined():
    """findMinimum function is defined in find-minimum.cpp and loop bounds are safe"""
    with open("find-minimum.cpp", "r") as f:
        code = f.read()
    
    # Remove comments
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    # Search for findMinimum signature
    if not re.search(r'\bint\s+findMinimum\s*\([^)]*\)', code_clean):
        raise check50.Failure(
            "Could not find function 'int findMinimum(int arr[], int size)' defined.",
            help="Define the function with the signature: int findMinimum(int arr[], int size) as shown in the slide."
        )

    # Check for <= size
    if re.search(r'<=\s*size\b', code_clean):
        raise check50.Failure(
            "Out of bounds array access detected in loop condition.",
            help="Make sure your loop condition uses '< size' instead of '<= size' to avoid accessing index equal to the array size (which is out of bounds)."
        )
