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
    """smallest-greater.cpp exists"""
    check50.exists("smallest-greater.cpp")

@check50.check(exists)
def test_compile():
    """smallest-greater.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG smallest-greater.cpp -o smallest-greater", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_example():
    """finds smallest element greater than 7 in {1, 7, 7, 10, 15}"""
    # Sorted version of example array: {1, 7, 7, 10, 15}. Smallest greater than 7 is 10 at index 3.
    check50.run("./smallest-greater").stdin("5\n1 7 7 10 15\n7", prompt=False).stdout("3", regex=False).exit(0)

@check50.check(test_compile)
def test_no_greater_exists():
    """returns -1 if no element is greater than target"""
    check50.run("./smallest-greater").stdin("5\n1 7 7 10 15\n25", prompt=False).stdout("-1", regex=False).exit(0)

@check50.check(test_compile)
def test_all_greater():
    """finds index 0 if target is smaller than all elements"""
    check50.run("./smallest-greater").stdin("4\n10 20 30 40\n5", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_middle_greater():
    """finds index of middle element"""
    check50.run("./smallest-greater").stdin("5\n5 10 15 20 25\n12", prompt=False).stdout("2", regex=False).exit(0)

@check50.check(test_compile)
def test_duplicates():
    """handles duplicate values correctly when searching for smallest greater"""
    check50.run("./smallest-greater").stdin("6\n2 2 5 5 8 8\n5", prompt=False).stdout("4", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles array of size 1"""
    check50.run("./smallest-greater").stdin("1\n99\n50", prompt=False).stdout("0", regex=False).exit(0)
    check50.run("./smallest-greater").stdin("1\n99\n100", prompt=False).stdout("-1", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """finds index of smallest greater in a random sorted array correctly"""
    n = random.randint(10, 50)
    arr = sorted([random.randint(-100, 100) for _ in range(n)])
    
    target = random.randint(-100, 100)
    expected_idx = -1
    for i, x in enumerate(arr):
        if x > target:
            expected_idx = i
            break
            
    stdin_data = f"{n}\n" + " ".join(map(str, arr)) + f"\n{target}"
    check50.run("./smallest-greater").stdin(stdin_data, prompt=False).stdout(str(expected_idx), regex=False).exit(0)

@check50.check(test_compile)
def test_function_defined():
    """findSmallestElementGreaterThan function is defined in smallest-greater.cpp"""
    with open("smallest-greater.cpp", "r") as f:
        code = f.read()
    
    # Remove comments
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    # Search for findSmallestElementGreaterThan signature
    if not re.search(r'\bint\s+findSmallestElementGreaterThan\s*\([^)]*\)', code_clean):
        raise check50.Failure(
            "Could not find function 'int findSmallestElementGreaterThan(int arr[], int size, int target)' defined.",
            help="Define the function with the signature: int findSmallestElementGreaterThan(int arr[], int size, int target) as shown in the slide."
        )
