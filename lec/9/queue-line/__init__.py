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
    """queue-line.cpp exists"""
    check50.exists("queue-line.cpp")

@check50.check(exists)
def test_compile():
    """queue-line.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG queue-line.cpp -o queue-line", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

@check50.check(test_compile)
def test_output():
    """simulates the serving order of Alice, Bob, and Charlie correctly"""
    expected_output = "Serving order:\nAlice\nBob\nCharlie"
    check50.run("./queue-line").stdout(expected_output, regex=False).exit(0)

@check50.check(test_compile)
def test_queue_used():
    """queue container is used in queue-line.cpp"""
    with open("queue-line.cpp", "r") as f:
        code = f.read()
    
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    if "queue" not in code_clean:
        raise check50.Failure("std::queue is not used in queue-line.cpp.")
