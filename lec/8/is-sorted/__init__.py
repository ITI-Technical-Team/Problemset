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
    """is-sorted.cpp exists"""
    check50.exists("is-sorted.cpp")

@check50.check(exists)
def test_compile():
    """is-sorted.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG is-sorted.cpp -o is-sorted", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_example_unsorted():
    """handles unsorted array {2, 1, 3, 1, 2} and outputs No"""
    check50.run("./is-sorted").stdin("5\n2 1 3 1 2", prompt=False).stdout("No", regex=False).exit(0)

@check50.check(test_compile)
def test_sorted():
    """handles sorted array {1, 2, 3, 4, 5} and outputs Yes"""
    check50.run("./is-sorted").stdin("5\n1 2 3 4 5", prompt=False).stdout("Yes", regex=False).exit(0)

@check50.check(test_compile)
def test_sorted_duplicates():
    """handles sorted array with duplicates {1, 2, 2, 3, 4} and outputs Yes"""
    check50.run("./is-sorted").stdin("5\n1 2 2 3 4", prompt=False).stdout("Yes", regex=False).exit(0)

@check50.check(test_compile)
def test_single_element():
    """handles single element array and outputs Yes"""
    check50.run("./is-sorted").stdin("1\n42", prompt=False).stdout("Yes", regex=False).exit(0)

@check50.check(test_compile)
def test_negative_sorted():
    """handles negative sorted array {-10, -5, -1, 0, 5} and outputs Yes"""
    check50.run("./is-sorted").stdin("5\n-10 -5 -1 0 5", prompt=False).stdout("Yes", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """checks random arrays correctly"""
    # Sorted case
    n = random.randint(10, 30)
    arr = sorted([random.randint(-100, 100) for _ in range(n)])
    stdin_data = f"{n}\n" + " ".join(map(str, arr))
    check50.run("./is-sorted").stdin(stdin_data, prompt=False).stdout("Yes", regex=False).exit(0)
    
    # Unsorted case
    arr_unsorted = [3, 1, 4, 1, 5, 9, 2]
    stdin_data2 = f"7\n" + " ".join(map(str, arr_unsorted))
    check50.run("./is-sorted").stdin(stdin_data2, prompt=False).stdout("No", regex=False).exit(0)

@check50.check(test_compile)
def test_function_defined():
    """isSorted function is defined in is-sorted.cpp and loop bounds are safe"""
    with open("is-sorted.cpp", "r") as f:
        code = f.read()
    
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    if not re.search(r'\bbool\s+isSorted\s*\([^)]*\)', code_clean):
        raise check50.Failure(
            "Could not find function 'bool isSorted(int arr[], int n)' defined.",
            help="Define the function with the signature: bool isSorted(int arr[], int n) as shown in the slide."
        )

    # Check for out of bounds loop condition where student goes up to n or n-1 (inclusive) while checking i+1
    if re.search(r'(?:i\s*<\s*(?:n|size)\b|i\s*<=\s*(?:n|size)\s*-\s*1)', code_clean):
        raise check50.Failure(
            "Out of bounds array access detected in loop condition.",
            help="Since you are comparing 'arr[i] > arr[i + 1]' inside the loop, the loop index must stop before the last element. Make sure your condition is 'i < n - 1' (or 'i < size - 1') to prevent accessing index 'i + 1' out of bounds."
        )
