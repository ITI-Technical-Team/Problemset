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
    """valid-parentheses.cpp exists"""
    check50.exists("valid-parentheses.cpp")

@check50.check(exists)
def test_compile():
    """valid-parentheses.cpp compiles successfully"""
    proc = check50.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG valid-parentheses.cpp -o valid-parentheses 2>&1")
    proc.stdout(output=None)
    proc.exit(0)

@check50.check(test_compile)
def test_examples_set1():
    """validates multiple sequences (Example set 1)"""
    check50.run("./valid-parentheses").stdin("3\n()\n((\n())(", prompt=False).stdout("YES\nNO\nNO", regex=False).exit(0)

@check50.check(test_compile)
def test_examples_set2():
    """validates multiple sequences (Example set 2)"""
    check50.run("./valid-parentheses").stdin("4\n)()(())\n()(((()\n(((())))\n(())(())", prompt=False).stdout("NO\nNO\nYES\nYES", regex=False).exit(0)

@check50.check(test_compile)
def test_mixed_cases():
    """handles mixed valid and invalid cases"""
    check50.run("./valid-parentheses").stdin("5\n()\n)(\n((()))\n(()))(\n()(())", prompt=False).stdout("YES\nNO\nYES\nNO\nYES", regex=False).exit(0)

@check50.check(test_compile)
def test_longer():
    """handles longer sequences"""
    check50.run("./valid-parentheses").stdin("2\n((((()))))(()())\n())(()", prompt=False).stdout("YES\nNO", regex=False).exit(0)

@check50.check(test_compile)
def test_minimal_size():
    """handles minimal parenthesized strings of length 1"""
    check50.run("./valid-parentheses").stdin("2\n(\n)", prompt=False).stdout("NO\nNO", regex=False).exit(0)


@check50.check(test_compile)
def test_random():
    """validates random parentheses sequences correctly"""
    t = random.randint(5, 15)
    inputs = []
    outputs = []
    for _ in range(t):
        if random.choice([True, False]):
            seq = []
            bal = 0
            for _ in range(random.randint(5, 15)):
                if bal == 0 or random.choice([True, False]):
                    seq.append("(")
                    bal += 1
                else:
                    seq.append(")")
                    bal -= 1
            seq.extend([")"] * bal)
            inputs.append("".join(seq))
            outputs.append("YES")
        else:
            seq = "".join(random.choices(["(", ")"], k=random.randint(10, 30)))
            bal = 0
            ok = True
            for c in seq:
                bal += (1 if c == "(" else -1)
                if bal < 0: ok = False
            if bal != 0: ok = False
            inputs.append(seq)
            outputs.append("YES" if ok else "NO")
    expected = "\n".join(outputs)
    stdin_data = f"{t}\n" + "\n".join(inputs)
    check50.run("./valid-parentheses").stdin(stdin_data, prompt=False).stdout(expected, regex=False).exit(0)
