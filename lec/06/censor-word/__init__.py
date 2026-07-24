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
    """censor-word.cpp exists"""
    check50.exists("censor-word.cpp")


@check50.check(exists)
def test_compile():
    """censor-word.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG censor-word.cpp -o censor-word", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)


@check50.check(test_compile)
def test_censoring():
    """replaces all occurrences of 'bad' with 'good' in 'I love bad food and bad drinks'"""
    run = check50.run("./censor-word").stdin("I love bad food and bad drinks", prompt=False).stdin("bad", prompt=False).stdin("good", prompt=False)
    
    expected = (
        "Enter text: "
        "Enter target: "
        "Enter replacement: "
        "Result: I love good food and good drinks"
    )
    run.stdout(expected, regex=False).exit(0)


@check50.check(test_compile)
def test_method_usage():
    """verifies that .find() and .replace() methods are used"""
    with open("censor-word.cpp", "r") as f:
        code = f.read()
    
    # Remove comments
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    if ".find" not in code_clean:
        raise check50.Failure(
            "Could not find the '.find' method used in censor-word.cpp.",
            help="Make sure you locate the target word using text.find(target)."
        )
        
    if ".replace" not in code_clean:
        raise check50.Failure(
            "Could not find the '.replace' method used in censor-word.cpp.",
            help="Make sure you replace the target word using text.replace(index, length, replacement)."
        )
