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
    """largest-smallest.cpp exists"""
    check50.exists("largest-smallest.cpp")

@check50.check(exists)
def test_compile():
    """largest-smallest.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG largest-smallest.cpp -o largest-smallest", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_example():
    """finds largest and smallest in array {2, 1, 3, 1, 2}"""
    check50.run("./largest-smallest").stdin("5\n2 1 3 1 2", prompt=False).stdout("Largest: 3\nSmallest: 1", regex=False).exit(0)

@check50.check(test_compile)
def test_single_element():
    """handles array with a single element"""
    check50.run("./largest-smallest").stdin("1\n42", prompt=False).stdout("Largest: 42\nSmallest: 42", regex=False).exit(0)

@check50.check(test_compile)
def test_negative_elements():
    """handles negative elements in array"""
    check50.run("./largest-smallest").stdin("4\n-10 -5 -20 -1", prompt=False).stdout("Largest: -1\nSmallest: -20", regex=False).exit(0)

@check50.check(test_compile)
def test_all_same():
    """handles array of identical elements"""
    check50.run("./largest-smallest").stdin("3\n7 7 7", prompt=False).stdout("Largest: 7\nSmallest: 7", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """finds largest and smallest in random array correctly"""
    n = random.randint(10, 50)
    arr = [random.randint(-1000, 1000) for _ in range(n)]
    expected = f"Largest: {max(arr)}\nSmallest: {min(arr)}"
    stdin_data = f"{n}\n" + " ".join(map(str, arr))
    check50.run("./largest-smallest").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_function_defined():
    """FindLargetAndSmallest or FindLargestAndSmallest function is defined"""
    with open("largest-smallest.cpp", "r") as f:
        code = f.read()
    
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    if not (re.search(r'\bvoid\s+FindLargetAndSmallest\s*\([^)]*\)', code_clean) or 
            re.search(r'\bvoid\s+FindLargestAndSmallest\s*\([^)]*\)', code_clean)):
        raise check50.Failure(
            "Could not find function 'void FindLargetAndSmallest(int arr[], int n)' defined.",
            help="Define the function with the signature: void FindLargetAndSmallest(int arr[], int n) as shown in the slide."
        )
