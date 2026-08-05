import check50
import string
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
    """one-string.cpp exists"""
    check50.exists("one-string.cpp")

@check50.check(exists)
def test_compile():
    """one-string.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG one-string.cpp -o one-string", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_example1():
    """concatenates 'string' and 'sheet'"""
    check50.run("./one-string").stdin("string\nsheet", prompt=False).stdout("stringsheet", regex=False).exit(0)

@check50.check(test_compile)
def test_extra1():
    """concatenates 'a' and 'b'"""
    check50.run("./one-string").stdin("a\nb", prompt=False).stdout("ab", regex=False).exit(0)

@check50.check(test_compile)
def test_extra2():
    """concatenates 'hello' and 'world'"""
    check50.run("./one-string").stdin("hello\nworld", prompt=False).stdout("helloworld", regex=False).exit(0)

@check50.check(test_compile)
def test_identical():
    """concatenates identical strings: 'same' and 'same'"""
    check50.run("./one-string").stdin("same\nsame", prompt=False).stdout("samesame", regex=False).exit(0)

@check50.check(test_compile)
def test_large():
    """concatenates two large strings of length 500 each"""
    check50.run("./one-string").stdin("x" * 500 + "\n" + "y" * 500, prompt=False).stdout("x" * 500 + "y" * 500, regex=False).exit(0)


@check50.check(test_compile)
def test_random():
    """concatenates random strings correctly"""
    s1 = "".join(random.choices(string.ascii_lowercase, k=10))
    s2 = "".join(random.choices(string.ascii_lowercase, k=10))
    expected = s1 + s2
    check50.run("./one-string").stdin(f"{s1}\n{s2}", prompt=False).stdout(expected, regex=False).exit(0)

@check50.check(test_compile)
def test_string_included():
    """string library is included in one-string.cpp"""
    with open("one-string.cpp", "r") as f:
        code = f.read()
    
    import re
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    if not re.search(r'#\s*include\s*[<"]string[>"]', code_clean):
        raise check50.Failure("Did not find #include <string> in one-string.cpp.")


@check50.check(test_compile)
def test_concatenation_used():
    """string concatenation operator (+) or append() function is used in one-string.cpp"""
    with open("one-string.cpp", "r") as f:
        code = f.read()
    
    import re
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    if not re.search(r'\+|\.\s*append\b', code_clean):
        raise check50.Failure(
            "String concatenation is not used in one-string.cpp.",
            help="You must concatenate the two strings using the '+' operator or '.append()' method rather than printing them side-by-side."
        )
