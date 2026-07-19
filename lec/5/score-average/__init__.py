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
    """score-average.cpp exists"""
    check50.exists("score-average.cpp")

@check50.check(exists)
def test_compile():
    """score-average.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG score-average.cpp -o score-average", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_example():
    """handles input: 5 and elements: 5 1 15 2 10"""
    run = check50.run("./score-average").stdin("5", prompt=False)
    for val in ["5", "1", "15", "2", "10"]:
        run.stdin(val, prompt=False)
    
    # sum = 33, count = 5, average = 6.60
    expected = (
        "Enter the number of elements : "
        "Enter element number 1 : "
        "Enter element number 2 : "
        "Enter element number 3 : "
        "Enter element number 4 : "
        "Enter element number 5 : "
        "average of scores : 6.60"
    )
    run.stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_precision():
    """verifies float number with 2 digits after decimal point"""
    run = check50.run("./score-average").stdin("3", prompt=False)
    for val in ["5", "5", "6"]:
        run.stdin(val, prompt=False)
        
    # sum = 16, count = 3, average = 5.33
    expected = (
        "Enter the number of elements : "
        "Enter element number 1 : "
        "Enter element number 2 : "
        "Enter element number 3 : "
        "average of scores : 5.33"
    )
    run.stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random inputs correctly"""
    n = random.randint(1, 20)
    elements = [random.randint(0, 100) for _ in range(n)]
    avg = sum(elements) / n
    expected_avg = f"{avg:.2f}"
    
    run = check50.run("./score-average").stdin(str(n), prompt=False)
    for val in elements:
        run.stdin(str(val), prompt=False)
        
    expected_parts = ["Enter the number of elements : "]
    for i in range(1, n + 1):
        expected_parts.append(f"Enter element number {i} : ")
    expected_parts.append(f"average of scores : {expected_avg}")
    
    run.stdout("".join(expected_parts), regex=False).exit(0)

@check50.check(test_compile)
def test_function_defined():
    """custom function is defined in score-average.cpp"""
    with open("score-average.cpp", "r") as f:
        code = f.read()
    
    # Remove single-line and multi-line comments
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    # Find all function definitions/declarations
    matches = re.findall(r'\b(int|long\s+long|void|double|float|std::string|string)\s+([a-zA-Z_]\w*)\s*\([^)]*\)\s*\{', code_clean)
    
    custom_functions = [name for _, name in matches if name != "main"]
    if not custom_functions:
        raise check50.Failure("Could not find a custom function defined (other than main) to compute the average as required by the problem description.")
