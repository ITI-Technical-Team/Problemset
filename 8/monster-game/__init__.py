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
    """monster-game.cpp exists"""
    check50.exists("monster-game.cpp")

@check50.check(exists)
def test_compile():
    """monster-game.cpp compiles successfully"""
    check50.run("g++ monster-game.cpp -fsanitize=bounds -fno-sanitize-recover=bounds -o monster-game").exit(0)

@check50.check(test_compile)
def test_example():
    """counts defeated monsters correctly (Example)"""
    check50.run("./monster-game").stdin("10\n5\n8 3 12 4 16", prompt=False).stdout("3", regex=False).exit(0)

@check50.check(test_compile)
def test_defeat_all():
    """handles case where player can defeat all monsters"""
    check50.run("./monster-game").stdin("100\n3\n10 20 30", prompt=False).stdout("3", regex=False).exit(0)

@check50.check(test_compile)
def test_defeat_none():
    """handles case where player cannot defeat any monsters"""
    check50.run("./monster-game").stdin("5\n4\n10 10 10 10", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_strict_greater():
    """handles strict inequality rule properly (must be strictly greater health)"""
    check50.run("./monster-game").stdin("10\n3\n9 10 11", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test_mixed_longer():
    """handles a longer list with mixed values"""
    # h = 12. Monsters: 11, 5, 7, 3, 1 (5 monsters) have health strictly less than 12.
    check50.run("./monster-game").stdin("12\n8\n11 5 13 7 12 3 1 20", prompt=False).stdout("5", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """counts defeated monsters in a random game correctly"""
    h = random.randint(1, 1000)
    n = random.randint(10, 50)
    monsters = [random.randint(1, 1500) for _ in range(n)]
    expected = str(sum(1 for x in monsters if x < h))
    stdin_data = f"{h}\n{n}\n" + " ".join(map(str, monsters))
    check50.run("./monster-game").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)
