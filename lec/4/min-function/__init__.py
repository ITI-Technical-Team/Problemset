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
            expected_str = str(output)
            out = super().stdout(output=None)
            if out.split() != expected_str.split():
                raise check50.Mismatch(expected_str, out)
            return self
        return super().stdout(output, *args, **kwargs)

check50.run = RobustRun

@check50.check()
def exists():
    """min-function.cpp exists"""
    check50.exists("min-function.cpp")

@check50.check(exists)
def test_compile():
    """min-function.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG min-function.cpp -o min-function", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_example():
    """handles input: 3 5"""
    check50.run("./min-function").stdin("3", prompt=False).stdin("5", prompt=False).stdout("3", regex=False).exit(0)

@check50.check(test_compile)
def test_negative():
    """handles input: 10 -2"""
    check50.run("./min-function").stdin("10", prompt=False).stdin("-2", prompt=False).stdout("-2", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """handles random inputs correctly"""
    x = random.randint(-1000, 1000)
    y = random.randint(-1000, 1000)
    expected = str(min(x, y))
    check50.run("./min-function").stdin(str(x), prompt=False).stdin(str(y), prompt=False).stdout(expected, regex=False).exit(0)


@check50.check(test_compile)
def test_function_defined():
    """custom function is defined and called in min-function.cpp"""
    import re
    with open("min-function.cpp", "r") as f:
        code = f.read()

    # Remove single-line and multi-line comments
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)

    # Find all non-void function definitions (must return a value)
    all_matches = re.findall(r'\b(int|long\s+long|void|double|float|std::string|string)\s+([a-zA-Z_]\w*)\s*\([^)]*\)\s*\{', code_clean)
    custom_functions = [(ret, name) for ret, name in all_matches if name != "main"]

    if not custom_functions:
        raise check50.Failure(
            "Could not find a custom function defined (other than main) as required by the problem description."
        )

    # Check that the custom function returns a value (not void)
    for ret_type, fn_name in custom_functions:
        if ret_type.strip() == "void":
            raise check50.Failure(
                f"Your function '{fn_name}' has return type 'void' — it should return the minimum value instead of printing it.",
                help=f"Change 'void {fn_name}(...)' to 'int {fn_name}(...)' and use 'return' to return the minimum value. Then print it in main()."
            )

    # Verify custom function is called in main
    main_match = re.search(r'\bint\s+main\s*\([^)]*\)\s*\{(.*)\}', code_clean, flags=re.DOTALL)
    if main_match:
        main_body = main_match.group(1)
        called = any(re.search(rf'\b{re.escape(fn)}\s*\(', main_body) for _, fn in custom_functions)
        if not called:
            fn_name = custom_functions[0][1]
            raise check50.Failure(
                f"Custom function '{fn_name}' is defined, but never called in main().",
                help=f"Make sure you call '{fn_name}(...)' inside main() instead of using built-in std::min."
            )

