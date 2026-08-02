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
    """word-search.cpp exists"""
    check50.exists("word-search.cpp")


@check50.check(exists)
def test_compile():
    """word-search.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG word-search.cpp -o word-search", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)


@check50.check(test_compile)
def test_found():
    """finds occurrence of 'welcome' in 'Hello world, welcome to C++ programming.'"""
    run = check50.run("./word-search").stdin("Hello world, welcome to C++ programming.", prompt=False).stdin("welcome", prompt=False)
    
    expected = (
        "Enter text: "
        "Enter word: "
        "Index: 13"
    )
    run.stdout(expected, regex=False).exit(0)


@check50.check(test_compile)
def test_not_found():
    """handles word not found: 'Hello world', 'java'"""
    run = check50.run("./word-search").stdin("Hello world", prompt=False).stdin("java", prompt=False)
    
    expected = (
        "Enter text: "
        "Enter word: "
        "Word not found"
    )
    run.stdout(expected, regex=False).exit(0)


@check50.check(test_compile)
def test_found_at_start():
    """finds occurrence of 'Hello' at index 0 in 'Hello world'"""
    run = check50.run("./word-search").stdin("Hello world", prompt=False).stdin("Hello", prompt=False)
    
    expected = (
        "Enter text: "
        "Enter word: "
        "Index: 0"
    )
    run.stdout(expected, regex=False).exit(0)


@check50.check(test_compile)
def test_method_usage():
    """verifies that .find() method is used and <string> header is included"""
    with open("word-search.cpp", "r") as f:
        code = f.read()
    
    # Remove comments
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)

    if not re.search(r'#include\s*<\s*string\s*>', code_clean):
        raise check50.Failure(
            "Missing #include <string>",
            help="Make sure to write '#include <string>' at the top of word-search.cpp when using std::string."
        )
    
    if ".find" not in code_clean:
        raise check50.Failure(
            "Could not find the '.find' method used in word-search.cpp.",
            help="Make sure you locate the word using text.find(word)."
        )
