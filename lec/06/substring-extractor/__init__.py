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
    """substring-extractor.cpp exists"""
    check50.exists("substring-extractor.cpp")


@check50.check(exists)
def test_compile():
    """substring-extractor.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG substring-extractor.cpp -o substring-extractor", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)


@check50.check(test_compile)
def test_valid_input():
    """handles valid input: 'Programming', 3, 5"""
    run = check50.run("./substring-extractor").stdin("Programming", prompt=False).stdin("3", prompt=False).stdin("5", prompt=False)
    
    expected = (
        "Enter text: "
        "Enter start index: "
        "Enter length: "
        "Original length: 11 "
        "Substring: gramm"
    )
    run.stdout(expected, regex=False).exit(0)


@check50.check(test_compile)
def test_start_index_zero():
    """handles starting index 0 correctly (e.g., 'Programming', 0, 5)"""
    run = check50.run("./substring-extractor").stdin("Programming", prompt=False).stdin("0", prompt=False).stdin("5", prompt=False)
    
    expected = (
        "Enter text: "
        "Enter start index: "
        "Enter length: "
        "Original length: 11 "
        "Substring: Progr"
    )
    run.stdout(expected, regex=False).exit(0)


@check50.check(test_compile)
def test_invalid_index():
    """handles invalid index input: 'Programming', 15, 2"""
    run = check50.run("./substring-extractor").stdin("Programming", prompt=False).stdin("15", prompt=False).stdin("2", prompt=False)
    
    expected = (
        "Enter text: "
        "Enter start index: "
        "Enter length: "
        "Original length: 11 "
        "Invalid index"
    )
    run.stdout(expected, regex=False).exit(0)


@check50.check(test_compile)
def test_negative_index():
    """handles invalid negative index input: 'Programming', -1, 5"""
    run = check50.run("./substring-extractor").stdin("Programming", prompt=False).stdin("-1", prompt=False).stdin("5", prompt=False)
    
    expected = (
        "Enter text: "
        "Enter start index: "
        "Enter length: "
        "Original length: 11 "
        "Invalid index"
    )
    run.stdout(expected, regex=False).exit(0)


@check50.check(test_compile)
def test_method_usage():
    """verifies that .substr() and .length() or .size() methods are used, and getline and <string> header are included"""
    with open("substring-extractor.cpp", "r") as f:
        code = f.read()
    
    # Remove comments
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)

    if not re.search(r'#include\s*<\s*string\s*>', code_clean):
        raise check50.Failure(
            "Missing #include <string>",
            help="Make sure to write '#include <string>' at the top of substring-extractor.cpp when using std::string."
        )

    if "getline" not in code_clean:
        raise check50.Failure(
            "Could not find the 'getline' function used in substring-extractor.cpp.",
            help="Make sure you read the line of text using getline(cin, text)."
        )
    
    if ".substr" not in code_clean:
        raise check50.Failure(
            "Could not find the '.substr' method used in substring-extractor.cpp.",
            help="Make sure you extract the substring using text.substr(start, length)."
        )
        
    if ".length" not in code_clean and ".size" not in code_clean:
        raise check50.Failure(
            "Could not find the '.length()' or '.size()' method used in substring-extractor.cpp.",
            help="Make sure you retrieve the string's length using length() or size() methods."
        )
