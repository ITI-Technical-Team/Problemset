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
    """stack.cpp exists"""
    check50.exists("stack.cpp")

@check50.check(exists)
def test_compile():
    """stack.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG stack.cpp -o stack", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_example():
    """processes stack operations correctly (Example)"""
    check50.run("./stack").stdin("5\n1 1\n1 2\n2\n2\n2", prompt=False).stdout("2\n1\nEmpty!", regex=False).exit(0)

@check50.check(test_compile)
def test_empty_then_use():
    """prints Empty! when popping an empty stack"""
    check50.run("./stack").stdin("4\n2\n1 5\n2\n2", prompt=False).stdout("Empty!\n5\nEmpty!", regex=False).exit(0)

@check50.check(test_compile)
def test_lifo():
    """checks LIFO ordering"""
    check50.run("./stack").stdin("6\n1 1\n1 2\n1 3\n2\n2\n2", prompt=False).stdout("3\n2\n1", regex=False).exit(0)

@check50.check(test_compile)
def test_interleaved():
    """handles interleaved push and pop"""
    check50.run("./stack").stdin("7\n1 10\n1 20\n2\n1 30\n2\n2\n2", prompt=False).stdout("20\n30\n10\nEmpty!", regex=False).exit(0)

@check50.check(test_compile)
def test_random():
    """simulates random stack operations correctly"""
    q = random.randint(10, 30)
    stack_data = []
    inputs = []
    outputs = []
    for _ in range(q):
        if random.choice([True, True, False]):
            x = random.randint(1, 1000)
            stack_data.append(x)
            inputs.append(f"1 {x}")
        else:
            inputs.append("2")
            if stack_data:
                outputs.append(str(stack_data.pop()))
            else:
                outputs.append("Empty!")
    expected = "\n".join(outputs)
    stdin_data = f"{q}\n" + "\n".join(inputs)
    check50.run("./stack").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)
