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
    """summation-2.cpp exists"""
    check50.exists("summation-2.cpp")

@check50.check(exists)
def test_compile():
    """summation-2.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG summation-2.cpp -o summation-2", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test1():
    """sums elements correctly (Example 1)"""
    check50.run("./summation-2").stdin("5\n1 5 3 2 4", prompt=False).stdout("15", regex=False).exit(0)

@check50.check(test_compile)
def test2():
    """sums elements correctly (Example 2)"""
    check50.run("./summation-2").stdin("7\n1 4 3 4 3 2 5", prompt=False).stdout("22", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles edge case N = 1 (minimal boundary)"""
    check50.run("./summation-2").stdin("1\n999", prompt=False).stdout("999", regex=False).exit(0)

@check50.check(test_compile)
def test_minimal_values():
    """handles edge case of minimal values (all 1s)"""
    check50.run("./summation-2").stdin("5\n1 1 1 1 1", prompt=False).stdout("5", regex=False).exit(0)

@check50.check(test_compile)
def test_maximal_values():
    """handles edge case of maximal bounds (N = 100, all 1000s)"""
    stdin_data = "100\n" + " ".join(["1000"] * 100)
    check50.run("./summation-2").stdin(stdin_data, prompt=False).stdout("100000", regex=False).exit(0)


@check50.check(test_compile)
def test_random():
    """sums random array correctly"""
    n = random.randint(10, 50)
    arr = [random.randint(-1000, 1000) for _ in range(n)]
    expected = str(sum(arr))
    stdin_data = f"{n}\n" + " ".join(map(str, arr))
    check50.run("./summation-2").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)


@check50.check(test_compile)
def test_function_defined():
    """custom function is defined and called in summation-2.cpp"""
    import re
    with open("summation-2.cpp", "r") as f:
        code = f.read()

    # Remove single-line and multi-line comments
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)

    # Find all function definitions/declarations
    all_matches = re.findall(r'\b(int|long\s+long|void|double|float|std::string|string)\s+([a-zA-Z_]\w*)\s*\([^)]*\)\s*\{', code_clean)
    custom_functions = [(ret, name) for ret, name in all_matches if name != "main"]

    if not custom_functions:
        raise check50.Failure("Could not find a custom function defined (other than main) as required by the problem description.")

    # Check that the custom function returns a value (not void)
    for ret_type, fn_name in custom_functions:
        if ret_type.strip() == "void":
            raise check50.Failure(
                f"Your function '{fn_name}' has return type 'void' — it should return the summation value instead of printing inside the function.",
                help=f"Change 'void {fn_name}(...)' to return a numeric type (e.g. int or long long) and use 'return'. Then print the result in main()."
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
                help=f"Make sure you call '{fn_name}(...)' inside main() and print its return value."
            )

