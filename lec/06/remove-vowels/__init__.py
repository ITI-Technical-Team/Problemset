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
    """remove-vowels.cpp exists"""
    check50.exists("remove-vowels.cpp")


@check50.check(exists)
def test_compile():
    """remove-vowels.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG remove-vowels.cpp -o remove-vowels", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)


@check50.check(test_compile)
def test_hello_world():
    """removes vowels from 'Hello World'"""
    run = check50.run("./remove-vowels").stdin("Hello World", prompt=False)
    
    expected = (
        "Enter text: "
        "Result: Hll Wrld"
    )
    run.stdout(expected, regex=False).exit(0)


@check50.check(test_compile)
def test_all_vowels():
    """removes all vowels from 'AEIOU'"""
    run = check50.run("./remove-vowels").stdin("AEIOU", prompt=False)
    
    expected = (
        "Enter text: "
        "Result: "
    )
    run.stdout(expected, regex=False).exit(0)


@check50.check(test_compile)
def test_no_vowels():
    """removes no letters from 'rhythm'"""
    run = check50.run("./remove-vowels").stdin("rhythm", prompt=False)
    
    expected = (
        "Enter text: "
        "Result: rhythm"
    )
    run.stdout(expected, regex=False).exit(0)


@check50.check(test_compile)
def test_method_usage():
    """verifies that .erase() method is used"""
    with open("remove-vowels.cpp", "r") as f:
        code = f.read()
    
    # Remove comments
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    if ".erase" not in code_clean:
        raise check50.Failure(
            "Could not find the '.erase' method used in remove-vowels.cpp.",
            help="Make sure you erase characters from the string using the erase() method."
        )
