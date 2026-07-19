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
    """scores-greater-than-10.cpp exists"""
    check50.exists("scores-greater-than-10.cpp")

@check50.check(exists)
def test_compile():
    """scores-greater-than-10.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG scores-greater-than-10.cpp -o scores-greater-than-10", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_example():
    """handles input: 5 and elements: 5 1 15 2 10"""
    run = check50.run("./scores-greater-than-10").stdin("5", prompt=False)
    for val in ["5", "1", "15", "2", "10"]:
        run.stdin(val, prompt=False)
    
    expected = (
        "Enter the number of elements : "
        "Enter element number 1 : "
        "Enter element number 2 : "
        "Enter element number 3 : "
        "Enter element number 4 : "
        "Enter element number 5 : "
        "number of scores greater than 10 : 1"
    )
    run.stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_none_greater():
    """handles case where no scores are greater than 10"""
    run = check50.run("./scores-greater-than-10").stdin("3", prompt=False)
    for val in ["10", "9", "5"]:
        run.stdin(val, prompt=False)
        
    expected = (
        "Enter the number of elements : "
        "Enter element number 1 : "
        "Enter element number 2 : "
        "Enter element number 3 : "
        "number of scores greater than 10 : 0"
    )
    run.stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random inputs correctly"""
    n = random.randint(1, 20)
    elements = [random.randint(0, 30) for _ in range(n)]
    count = sum(1 for x in elements if x > 10)
    
    run = check50.run("./scores-greater-than-10").stdin(str(n), prompt=False)
    for val in elements:
        run.stdin(str(val), prompt=False)
        
    expected_parts = ["Enter the number of elements : "]
    for i in range(1, n + 1):
        expected_parts.append(f"Enter element number {i} : ")
    expected_parts.append(f"number of scores greater than 10 : {count}")
    
    run.stdout("".join(expected_parts), regex=False).exit(0)

@check50.check(test_compile)
def test_array_used():
    """verifies that an array is declared and used in scores-greater-than-10.cpp"""
    with open("scores-greater-than-10.cpp", "r") as f:
        code = f.read()
        
    # Remove comments
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    # Matches syntax like: int scores[100]; or int scores[n]; or double arr[]
    # Also matches std::vector or std::array
    has_raw_array = re.search(r'\b(int|long|double|float|string)\s+[a-zA-Z_]\w*\s*\[\s*[^\]]*\s*\]', code_clean)
    has_std_array = re.search(r'\b(std::)?array\s*<', code_clean)
    has_std_vector = re.search(r'\b(std::)?vector\s*<', code_clean)
    
    if not (has_raw_array or has_std_array or has_std_vector):
        raise check50.Failure("You must use an array, vector, or std::array to store and process the scores as required by the problem instructions.")
