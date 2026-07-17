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
    """a-to-e.cpp exists"""
    check50.exists("a-to-e.cpp")

@check50.check(exists)
def test_compile():
    """a-to-e.cpp compiles successfully"""
    check50.run("g++ -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG a-to-e.cpp -o a-to-e").exit(0)

@check50.check(test_compile)
def test_example1():
    """handles input: 3 ace"""
    check50.run("./a-to-e").stdin("3\nace", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_extra1():
    """handles input: 4 abcf (with invalid char 'f')"""
    check50.run("./a-to-e").stdin("4\nabcf", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_extra2():
    """handles input: 5 abcde (all valid chars)"""
    check50.run("./a-to-e").stdin("5\nabcde", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_extra3():
    """handles input: 1 z"""
    check50.run("./a-to-e").stdin("1\nz", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_minimal_yes():
    """handles minimal input: 1 a"""
    check50.run("./a-to-e").stdin("1\na", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_minimal_no():
    """handles minimal input: 1 f"""
    check50.run("./a-to-e").stdin("1\nf", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_large_yes():
    """handles large valid string N = 1000"""
    check50.run("./a-to-e").stdin("1000\n" + "e" * 1000, prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_large_no():
    """handles large string N = 1000 with invalid character at the end"""
    check50.run("./a-to-e").stdin("1000\n" + "e" * 999 + "f", prompt=False).stdout("NO", regex=False).exit(0)


@check50.check(test_compile)
def test_random_yes():
    """handles string with only 'a'-'e' correctly"""
    n = random.randint(5, 20)
    s = "".join(random.choices("abcde", k=n))
    check50.run("./a-to-e").stdin(f"{n}\n{s}", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_random_no():
    """handles string with other characters correctly"""
    n = random.randint(5, 20)
    s = "".join(random.choices("abcde", k=n-1)) + "f"
    check50.run("./a-to-e").stdin(f"{n}\n{s}", prompt=False).stdout("NO", regex=False).exit(0)
