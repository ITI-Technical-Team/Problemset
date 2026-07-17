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
            expected_str = str(output).strip()
            out = super().stdout(output=None).strip()
            if out.split() != expected_str.split():
                raise check50.Mismatch(expected_str, out)
            return self
        return super().stdout(output, *args, **kwargs)

check50.run = RobustRun

@check50.check()
def exists():
    """print-hello.cpp exists"""
    check50.exists("print-hello.cpp")

@check50.check(exists)
def test_compile():
    """print-hello.cpp compiles successfully"""
    check50.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG print-hello.cpp -o print-hello").exit(0)

@check50.check(test_compile)
def test_three():
    """handles input: 3"""
    expected = "\n".join("Hello, World" for _ in range(3))
    check50.run("./print-hello").stdin("3", prompt=False).stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_one():
    """handles input: 1"""
    check50.run("./print-hello").stdin("1", prompt=False).stdout("Hello, World", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random inputs correctly"""
    n = random.randint(1, 20)
    expected = "\n".join("Hello, World" for _ in range(n))
    check50.run("./print-hello").stdin(str(n), prompt=False).stdout(expected, regex=False).exit(0)


@check50.check(test_compile)
def test_function_defined():
    """custom function is defined in print-hello.cpp"""
    import re
    with open("print-hello.cpp", "r") as f:
        code = f.read()
    
    # Remove single-line and multi-line comments
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    # Find all function definitions/declarations
    matches = re.findall(r'\b(int|long\s+long|void|double|float|std::string|string)\s+([a-zA-Z_]\w*)\s*\([^)]*\)\s*\{', code_clean)
    
    custom_functions = [name for _, name in matches if name != "main"]
    if not custom_functions:
        raise check50.Failure("Could not find a custom function defined (other than main) as required by the problem description.")
