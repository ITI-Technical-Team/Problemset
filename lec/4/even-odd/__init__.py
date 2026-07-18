import check50
import random

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
            expected_str = str(output).strip().lower()
            out = super().stdout(output=None).strip().lower()
            if out != expected_str:
                raise check50.Mismatch(expected_str, out)
            return self
        return super().stdout(output, *args, **kwargs)

check50.run = RobustRun

@check50.check()
def exists():
    """even-odd.cpp exists"""
    check50.exists("even-odd.cpp")

@check50.check(exists)
def test_compile():
    """even-odd.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG even-odd.cpp -o even-odd", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_two():
    """handles input: 2"""
    check50.run("./even-odd").stdin("2", prompt=False).stdout("Even", regex=False).exit(0)

@check50.check(test_compile)
def test_five():
    """handles input: 5"""
    check50.run("./even-odd").stdin("5", prompt=False).stdout("Odd", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random inputs correctly"""
    n = random.randint(-1000, 1000)
    expected = "Even" if n % 2 == 0 else "Odd"
    check50.run("./even-odd").stdin(str(n), prompt=False).stdout(expected, regex=False).exit(0)


@check50.check(test_compile)
def test_function_defined():
    """custom function is defined in even-odd.cpp"""
    import re
    with open("even-odd.cpp", "r") as f:
        code = f.read()
    
    # Remove single-line and multi-line comments
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    # Find all function definitions/declarations
    matches = re.findall(r'\b(int|long\s+long|void|double|float|std::string|string)\s+([a-zA-Z_]\w*)\s*\([^)]*\)\s*\{', code_clean)
    
    custom_functions = [name for _, name in matches if name != "main"]
    if not custom_functions:
        raise check50.Failure("Could not find a custom function defined (other than main) as required by the problem description.")
