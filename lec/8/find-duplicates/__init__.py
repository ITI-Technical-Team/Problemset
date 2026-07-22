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
    """find-duplicates.cpp exists"""
    check50.exists("find-duplicates.cpp")

@check50.check(exists)
def test_compile():
    """find-duplicates.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG find-duplicates.cpp -o find-duplicates", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_example():
    """finds duplicates for array {1, 2, 3, 2, 4, 3, 5, 1} and outputs 1 2 3"""
    check50.run("./find-duplicates").stdin("8\n1 2 3 2 4 3 5 1", prompt=False).stdout("1 2 3", regex=False).exit(0)

@check50.check(test_compile)
def test_no_duplicates():
    """outputs empty line or nothing when there are no duplicates"""
    check50.run("./find-duplicates").stdin("4\n1 2 3 4", prompt=False).stdout("", regex=False).exit(0)

@check50.check(test_compile)
def test_multiple_identical_duplicates():
    """outputs each duplicate value exactly once even if it appears more than twice"""
    check50.run("./find-duplicates").stdin("6\n2 2 2 3 3 3", prompt=False).stdout("2 3", regex=False).exit(0)

@check50.check(test_compile)
def test_sorted_output():
    """prints duplicates in ascending sorted order regardless of array order"""
    check50.run("./find-duplicates").stdin("6\n5 2 5 2 1 1", prompt=False).stdout("1 2 5", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """finds duplicates in random array correctly"""
    n = random.randint(10, 40)
    arr = [random.randint(-100, 100) for _ in range(n)]
    
    # Calculate duplicates
    seen = set()
    dups = set()
    for x in arr:
        if x in seen:
            dups.add(x)
        else:
            seen.add(x)
    expected = " ".join(map(str, sorted(list(dups))))
    stdin_data = f"{n}\n" + " ".join(map(str, arr))
    check50.run("./find-duplicates").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_function_defined():
    """findDuplicates function is defined in find-duplicates.cpp"""
    with open("find-duplicates.cpp", "r") as f:
        code = f.read()
    
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    if not re.search(r'\bvoid\s+findDuplicates\s*\([^)]*\)', code_clean):
        raise check50.Failure(
            "Could not find function 'void findDuplicates(int arr[], int n)' defined.",
            help="Define the function with the signature: void findDuplicates(int arr[], int n) to modularize your logic."
        )
