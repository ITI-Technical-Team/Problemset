import check50
import random
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
            expected_str = str(output)
            out = super().stdout(output=None)
            if out.split() != expected_str.split():
                raise check50.Mismatch(expected_str, out)
            return self
        return super().stdout(output, *args, **kwargs)

check50.run = RobustRun

@check50.check()
def exists():
    """palindrome.cpp exists"""
    check50.exists("palindrome.cpp")

@check50.check(exists)
def test_compile():
    """palindrome.cpp compiles successfully"""
    check50.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG palindrome.cpp -o palindrome 2>&1").exit(0)

@check50.check(test_compile)
def test_example1():
    """handles input: abba"""
    check50.run("./palindrome").stdin("abba", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_example2():
    """handles input: newcomers"""
    check50.run("./palindrome").stdin("newcomers", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_example3():
    """handles input: mam"""
    check50.run("./palindrome").stdin("mam", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_single_char():
    """handles single character: 'a'"""
    check50.run("./palindrome").stdin("a", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_two_char_yes():
    """handles 2-character string: 'aa'"""
    check50.run("./palindrome").stdin("aa", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_two_char_no():
    """handles 2-character string: 'ab'"""
    check50.run("./palindrome").stdin("ab", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_large_yes():
    """handles large palindrome of length 1000"""
    check50.run("./palindrome").stdin("a" * 1000, prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_large_no():
    """handles large non-palindrome of length 1000"""
    check50.run("./palindrome").stdin("a" * 500 + "b" + "a" * 499, prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_random_yes():
    """handles random palindromes correctly"""
    half = "".join(random.choices(string.ascii_lowercase, k=15))
    pal = half + half[::-1]
    check50.run("./palindrome").stdin(pal, prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_random_no():
    """handles random non-palindromes correctly"""
    half = "".join(random.choices(string.ascii_lowercase, k=15))
    non_pal = half + "xy" + half[::-1]
    check50.run("./palindrome").stdin(non_pal, prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_random_yes():
    """handles random palindromes correctly"""
    half = "".join(random.choices(string.ascii_lowercase, k=15))
    pal = half + half[::-1]
    check50.run("./palindrome").stdin(pal, prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_random_no():
    """handles random non-palindromes correctly"""
    half = "".join(random.choices(string.ascii_lowercase, k=15))
    non_pal = half + "xy" + half[::-1]
    check50.run("./palindrome").stdin(non_pal, prompt=False).stdout("NO", regex=False).exit(0)
