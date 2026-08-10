import check50
import random
import re
import string

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
    """reverse-string.cpp exists"""
    check50.exists("reverse-string.cpp")

@check50.check(exists)
def test_compile():
    """reverse-string.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG reverse-string.cpp -o reverse-string", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_example():
    """reverses the string 'hello' to 'olleh'"""
    check50.run("./reverse-string").stdin("hello", prompt=False).stdout("olleh", regex=False).exit(0)

@check50.check(test_compile)
def test_with_spaces():
    """reverses string with spaces 'hello world' to 'dlrow olleh'"""
    check50.run("./reverse-string").stdin("hello world", prompt=False).stdout("dlrow olleh", regex=False).exit(0)

@check50.check(test_compile)
def test_palindrome():
    """handles palindrome string 'racecar'"""
    check50.run("./reverse-string").stdin("racecar", prompt=False).stdout("racecar", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """reverses a random string correctly"""
    chars = string.ascii_letters + " "
    s = "".join(random.choice(chars) for _ in range(20))
    # Remove leading/trailing spaces to avoid split mismatch on ends
    s = s.strip()
    expected = s[::-1]
    check50.run("./reverse-string").stdin(s, prompt=False).stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_stack_used():
    """stack container and string library are used in reverse-string.cpp"""
    with open("reverse-string.cpp", "r") as f:
        code = f.read()
    
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    if not re.search(r'#include\s*<\s*string\s*>', code_clean):
        raise check50.Failure(
            "reverse-string.cpp does not include the <string> library.",
            help="Add '#include <string>' at the top of your file to use strings properly."
        )

    match = re.search(r'stack\s*<\s*[^>]*\s*>\s*([a-zA-Z0-9_]+)', code_clean)
    if not match:
        raise check50.Failure("std::stack is not used in reverse-string.cpp.")
        
    var_name = match.group(1)
    
    if not re.search(rf'{var_name}\s*\.\s*push', code_clean) or not re.search(rf'{var_name}\s*\.\s*pop', code_clean):
        raise check50.Failure(
            f"std::stack variable '{var_name}' is declared but not pushed to or popped from.",
            help="You must push all characters of the string onto the stack and pop them one by one to reverse it."
        )
