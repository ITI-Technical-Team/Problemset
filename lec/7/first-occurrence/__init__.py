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
    """first-occurrence.cpp exists"""
    check50.exists("first-occurrence.cpp")

@check50.check(exists)
def test_compile():
    """first-occurrence.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG first-occurrence.cpp -o first-occurrence", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_example():
    """finds first occurrence in sorted array {1, 7, 7, 15, 20} with target 7"""
    check50.run("./first-occurrence").stdin("5\n1 7 7 15 20\n7", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test_not_found():
    """returns -1 if target is not in the array"""
    check50.run("./first-occurrence").stdin("5\n1 7 7 15 20\n10", prompt=False).stdout("-1", regex=False).exit(0)

@check50.check(test_compile)
def test_first_element():
    """finds target at index 0"""
    check50.run("./first-occurrence").stdin("5\n1 7 7 15 20\n1", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_last_element():
    """finds target at last index"""
    check50.run("./first-occurrence").stdin("5\n1 7 7 15 20\n20", prompt=False).stdout("4", regex=False).exit(0)

@check50.check(test_compile)
def test_all_duplicates():
    """finds first index when all elements are duplicates"""
    check50.run("./first-occurrence").stdin("6\n5 5 5 5 5 5\n5", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles array of size 1"""
    check50.run("./first-occurrence").stdin("1\n99\n99", prompt=False).stdout("0", regex=False).exit(0)
    check50.run("./first-occurrence").stdin("1\n99\n5", prompt=False).stdout("-1", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """finds first occurrence in a random sorted array correctly"""
    n = random.randint(10, 50)
    arr = sorted([random.randint(-100, 100) for _ in range(n)])
    
    if random.choice([True, False]):
        target = random.choice(arr)
        expected = str(arr.index(target))
    else:
        target = 999
        expected = "-1"
        
    stdin_data = f"{n}\n" + " ".join(map(str, arr)) + f"\n{target}"
    check50.run("./first-occurrence").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_function_defined():
    """findFirstOccurrence function is defined in first-occurrence.cpp and loop bounds are safe"""
    with open("first-occurrence.cpp", "r") as f:
        code = f.read()
    
    # Remove comments
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    # Search for findFirstOccurrence signature
    if not re.search(r'\bint\s+findFirstOccurrence\s*\([^)]*\)', code_clean):
        raise check50.Failure(
            "Could not find function 'int findFirstOccurrence(int arr[], int size, int target)' defined.",
            help="Define the function with the signature: int findFirstOccurrence(int arr[], int size, int target) as shown in the slide."
        )

    # Check for <= size
    if re.search(r'<=\s*size\b', code_clean):
        raise check50.Failure(
            "Out of bounds array access detected in loop condition.",
            help="Make sure your loop condition uses '< size' instead of '<= size' to avoid accessing index equal to the array size (which is out of bounds)."
        )
