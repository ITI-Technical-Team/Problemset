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
    """dynamic-array.cpp exists"""
    check50.exists("dynamic-array.cpp")

@check50.check(exists)
def test_compile():
    """dynamic-array.cpp compiles successfully"""
    proc = check50.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG dynamic-array.cpp -o dynamic-array 2>&1")
    proc.stdout(output=None)
    proc.exit(0)

@check50.check(test_compile)
def test_example():
    """prints sequence order correctly (Example)"""
    check50.run("./dynamic-array").stdin("5\n13\n2\n7\n11\n20\n-1", prompt=False).stdout("5 13 2 7 11 20", regex=False).exit(0)

@check50.check(test_compile)
def test_single_value():
    """handles a single value before sentinel"""
    check50.run("./dynamic-array").stdin("42\n-1", prompt=False).stdout("42", regex=False).exit(0)

@check50.check(test_compile)
def test_duplicates():
    """handles duplicates and preserves order"""
    check50.run("./dynamic-array").stdin("3\n3\n3\n7\n3\n-1", prompt=False).stdout("3 3 3 7 3", regex=False).exit(0)

@check50.check(test_compile)
def test_longer_mixed():
    """handles longer mixed sequence"""
    check50.run("./dynamic-array").stdin("8\n1000000000\n1\n999\n5\n12\n12\n7\n2\n-1", prompt=False).stdout("8 1000000000 1 999 5 12 12 7 2", regex=False).exit(0)

@check50.check(test_compile)
def test_immediate_sentinel():
    """handles empty input sequence (sentinel at start)"""
    check50.run("./dynamic-array").stdin("-1", prompt=False).stdout("", regex=False).exit(0)


@check50.check(test_compile)
def test_random():
    """prints random sequence of numbers correctly"""
    n = random.randint(5, 30)
    arr = [random.randint(1, 1000) for _ in range(n)]
    expected = " ".join(map(str, arr))
    stdin_data = "\n".join(map(str, arr)) + "\n-1"
    check50.run("./dynamic-array").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)
