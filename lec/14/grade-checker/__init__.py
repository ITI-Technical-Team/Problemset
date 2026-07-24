import check50
import re
import subprocess


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _strip_js_comments(code):
    code = re.sub(r'//[^\n]*', '', code)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    return code


def _run_test(code, grade_val):
    # Regex to replace let/const/var grade = ...; with let grade = grade_val;
    # Matches declarations like: let grade = 85; or const grade=85
    pattern = r'\b(let|const|var)?\s*grade\s*=[^;\n]+'
    modified, count = re.subn(pattern, f'let grade = {grade_val}', code, count=1)
    if count == 0:
        modified = f"let grade = {grade_val};\n" + code

    # Execute code under node
    res = subprocess.run(["node", "-e", modified], capture_output=True, text=True)
    return res


# ─── existence & structure ────────────────────────────────────────────────────

@check50.check()
def exists():
    """grade-checker.js exists"""
    check50.exists("grade-checker.js")


@check50.check(exists)
def checks_if_statements():
    """JavaScript code uses if, else if, and else statements"""
    code = _read("grade-checker.js")
    clean = _strip_js_comments(code)

    if "if" not in clean:
        raise check50.Failure(
            "Missing 'if' statement",
            help="Use 'if' to check the grade (e.g. if (grade >= 90) { ... })"
        )
    if "else" not in clean:
        raise check50.Failure(
            "Missing 'else' / 'else if' statement",
            help="Use 'else if' and 'else' to cover multiple grade ranges"
        )


@check50.check(checks_if_statements)
def test_excellent():
    """displays 'Excellent' for grades >= 90"""
    code = _read("grade-checker.js")
    for val in [90, 95, 100]:
        res = _run_test(code, val)
        if res.returncode != 0:
            raise check50.Failure("JavaScript execution error", help=res.stderr.strip())
        out = res.stdout.strip().lower()
        if "excellent" not in out:
            raise check50.Failure(
                f"Incorrect output for grade {val}",
                help=f"Expected output to contain 'Excellent' for grade {val}, but got '{res.stdout.strip()}'"
            )


@check50.check(checks_if_statements)
def test_good():
    """displays 'Good' for grades from 75 to 89"""
    code = _read("grade-checker.js")
    for val in [75, 80, 89]:
        res = _run_test(code, val)
        if res.returncode != 0:
            raise check50.Failure("JavaScript execution error", help=res.stderr.strip())
        out = res.stdout.strip().lower()
        if "good" not in out:
            raise check50.Failure(
                f"Incorrect output for grade {val}",
                help=f"Expected output to contain 'Good' for grade {val}, but got '{res.stdout.strip()}'"
            )


@check50.check(checks_if_statements)
def test_pass():
    """displays 'Pass' for grades from 50 to 74"""
    code = _read("grade-checker.js")
    for val in [50, 60, 74]:
        res = _run_test(code, val)
        if res.returncode != 0:
            raise check50.Failure("JavaScript execution error", help=res.stderr.strip())
        out = res.stdout.strip().lower()
        if "pass" not in out:
            raise check50.Failure(
                f"Incorrect output for grade {val}",
                help=f"Expected output to contain 'Pass' for grade {val}, but got '{res.stdout.strip()}'"
            )


@check50.check(checks_if_statements)
def test_fail():
    """displays 'Fail' for grades < 50"""
    code = _read("grade-checker.js")
    for val in [0, 20, 49]:
        res = _run_test(code, val)
        if res.returncode != 0:
            raise check50.Failure("JavaScript execution error", help=res.stderr.strip())
        out = res.stdout.strip().lower()
        if "fail" not in out:
            raise check50.Failure(
                f"Incorrect output for grade {val}",
                help=f"Expected output to contain 'Fail' for grade {val}, but got '{res.stdout.strip()}'"
            )
