import check50
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
    """sort-descending.cpp exists"""
    check50.exists("sort-descending.cpp")

@check50.check(exists)
def test_compile():
    """sort-descending.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG sort-descending.cpp -o sort-descending", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_output():
    """displays the array elements in descending order"""
    expected = "Numbers in descending order: 70 60 50 40 30 20 10"
    check50.run("./sort-descending").stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_array_used():
    """verifies that an array is declared with the specified elements"""
    with open("sort-descending.cpp", "r") as f:
        code = f.read()
        
    # Remove comments
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    # Check for array declaration of size 7 containing the numbers
    has_array = re.search(r'\b(int|long|double|float)\s+[a-zA-Z_]\w*\s*\[\s*7\s*\]\s*=\s*\{\s*10\s*,\s*20\s*,\s*30\s*,\s*40\s*,\s*50\s*,\s*60\s*,\s*70\s*\}', code_clean)
    has_array_implicit = re.search(r'\b(int|long|double|float)\s+[a-zA-Z_]\w*\s*\[\s*\]\s*=\s*\{\s*10\s*,\s*20\s*,\s*30\s*,\s*40\s*,\s*50\s*,\s*60\s*,\s*70\s*\}', code_clean)
    
    if not (has_array or has_array_implicit):
        raise check50.Failure("Could not find the expected array declaration '{10, 20, 30, 40, 50, 60, 70}' in sort-descending.cpp.")
