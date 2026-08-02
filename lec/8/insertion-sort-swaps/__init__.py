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
    """insertion-sort-swaps.cpp exists"""
    check50.exists("insertion-sort-swaps.cpp")

@check50.check(exists)
def test_compile():
    """insertion-sort-swaps.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG insertion-sort-swaps.cpp -o insertion-sort-swaps", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_example():
    """counts swaps for array {2, 1, 3, 1, 2} and outputs 4"""
    check50.run("./insertion-sort-swaps").stdin("5\n2 1 3 1 2", prompt=False).stdout("4", regex=False).exit(0)

@check50.check(test_compile)
def test_sorted():
    """counts swaps for already sorted array and outputs 0"""
    check50.run("./insertion-sort-swaps").stdin("5\n1 2 3 4 5", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_reverse():
    """counts swaps for reverse-sorted array and outputs 10"""
    check50.run("./insertion-sort-swaps").stdin("5\n5 4 3 2 1", prompt=False).stdout("10", regex=False).exit(0)

@check50.check(test_compile)
def test_single_element():
    """counts swaps for array of size 1 and outputs 0"""
    check50.run("./insertion-sort-swaps").stdin("1\n99", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """counts swaps for random array correctly"""
    def insertion_sort_swaps(arr):
        swaps = 0
        a = list(arr)
        for i in range(1, len(a)):
            key = a[i]
            j = i - 1
            while j >= 0 and a[j] > key:
                a[j + 1] = a[j]
                j -= 1
                swaps += 1
            a[j + 1] = key
        return swaps

    n = random.randint(10, 30)
    arr = [random.randint(-100, 100) for _ in range(n)]
    expected = str(insertion_sort_swaps(arr))
    stdin_data = f"{n}\n" + " ".join(map(str, arr))
    check50.run("./insertion-sort-swaps").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_function_defined():
    """insertionSortSwaps function is defined in insertion-sort-swaps.cpp and loop bounds are safe"""
    with open("insertion-sort-swaps.cpp", "r") as f:
        code = f.read()
    
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    if not re.search(r'\bint\s+insertionSortSwaps\s*\([^)]*\)', code_clean):
        raise check50.Failure(
            "Could not find function 'int insertionSortSwaps(int arr[], int n)' defined.",
            help="Define the function with the signature: int insertionSortSwaps(int arr[], int n) as shown in the slide."
        )

    # Check for out of bounds loop condition where student goes up to n (inclusive)
    match_func = re.search(r'\bint\s+insertionSortSwaps\s*\([^)]*\)\s*\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}', code_clean)
    if match_func:
        func_body = match_func.group(0)
        if re.search(r'<=\s*(?:n|size)\b', func_body):
            raise check50.Failure(
                "Out of bounds array access detected in loop condition.",
                help="Make sure your outer loop condition is 'i < n' (or 'i < size') instead of '<=' to avoid out-of-bounds access."
            )
