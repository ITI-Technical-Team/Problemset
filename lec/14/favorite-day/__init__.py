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


def _run_test(code, day_val):
    val_str = str(day_val) if isinstance(day_val, int) else f'"{day_val}"'
    pattern = r'\b(let|const|var)?\s*day\s*=[^;\n]+'
    modified, count = re.subn(pattern, f'let day = {val_str}', code, count=1)
    if count == 0:
        modified = f"let day = {val_str};\n" + code

    res = subprocess.run(["node", "-e", modified], capture_output=True, text=True)
    return res


# ─── existence & structure ────────────────────────────────────────────────────

@check50.check()
def exists():
    """favorite-day.js exists"""
    check50.exists("favorite-day.js")


@check50.check(exists)
def checks_switch_statement():
    """JavaScript code uses a switch statement with break statements and default case"""
    code = _read("favorite-day.js")
    clean = _strip_js_comments(code)

    if "switch" not in clean:
        raise check50.Failure(
            "Missing 'switch' statement",
            help="Use a switch statement to select the day name (e.g. switch(day) { ... })"
        )
    if "break" not in clean:
        raise check50.Failure(
            "Missing 'break' statements in switch cases",
            help="Add 'break;' at the end of each switch case to prevent fallthrough to subsequent cases"
        )
    if "default" not in clean:
        raise check50.Failure(
            "Missing 'default' case in switch statement",
            help="Add a 'default:' case to handle invalid day inputs"
        )


@check50.check(checks_switch_statement)
def test_valid_days():
    """displays correct single day name for inputs 1 to 7"""
    code = _read("favorite-day.js")
    days_map = {
        1: "Sunday",
        2: "Monday",
        3: "Tuesday",
        4: "Wednesday",
        5: "Thursday",
        6: "Friday",
        7: "Saturday"
    }
    for val, expected in days_map.items():
        res = _run_test(code, val)
        if res.returncode != 0:
            raise check50.Failure("JavaScript execution error", help=res.stderr.strip())
        
        output_lines = [l.strip() for l in res.stdout.strip().splitlines() if l.strip()]
        if not output_lines:
            raise check50.Failure(
                f"No output for day {val}",
                help=f"Expected output to print '{expected}' for day {val}"
            )
        if len(output_lines) > 1:
            raise check50.Failure(
                f"Multiple lines output for day {val}: {output_lines}",
                help=f"Expected only '{expected}' to be printed for day {val}. Make sure each case ends with a 'break;' statement to prevent fallthrough!"
            )
            
        out = output_lines[0].lower()
        if expected.lower() not in out:
            raise check50.Failure(
                f"Incorrect output for day {val}",
                help=f"Expected output to be '{expected}' for day {val}, but got '{output_lines[0]}'"
            )


@check50.check(checks_switch_statement)
def test_invalid_days():
    """displays default error message for invalid inputs"""
    code = _read("favorite-day.js")
    for val in [0, 8, "invalid"]:
        res = _run_test(code, val)
        if res.returncode != 0:
            raise check50.Failure("JavaScript execution error", help=res.stderr.strip())
        out = res.stdout.strip().lower()
        
        if not out:
            raise check50.Failure(
                f"No output for invalid day '{val}'",
                help="Make sure the 'default:' case prints an error message (e.g. 'Invalid day')"
            )
            
        for day_name in ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]:
            if day_name in out:
                raise check50.Failure(
                    f"Output contains day name for invalid day '{val}'",
                    help=f"Expected default error message for input '{val}', but output contained '{day_name}'"
                )
