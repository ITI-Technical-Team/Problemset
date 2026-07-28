import check50
import random

@check50.check()
def exists():
    """circle.cpp exists"""
    check50.exists("circle.cpp")

@check50.check(exists)
def test_compile():
    """circle.cpp compiles successfully"""
    import subprocess as _sp
    _res = _sp.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG circle.cpp -o circle", shell=True, capture_output=True, text=True)
    if _res.returncode != 0:
        raise check50.Failure(_res.stderr or _res.stdout)

def verify_circle_output(out, r):
    tokens = out.split()
    
    # Verify Area
    if "Area" not in tokens:
        raise check50.Mismatch("Output containing 'Area = ...'", out)
    idx_area = tokens.index("Area")
    if idx_area + 2 >= len(tokens) or tokens[idx_area+1] != "=":
        raise check50.Mismatch("Output format: 'Area = <value>'", out)
    try:
        student_area = float(tokens[idx_area+2])
    except ValueError:
        raise check50.Mismatch("A numeric value for Area", tokens[idx_area+2])
    expected_area = 3.14 * r * r
    if abs(student_area - expected_area) > 1e-4:
        raise check50.Mismatch(f"Area = {expected_area}", f"Area = {student_area}")
        
    # Verify Perimeter
    if "Perimeter" not in tokens:
        raise check50.Mismatch("Output containing 'Perimeter = ...'", out)
    idx_perim = tokens.index("Perimeter")
    if idx_perim + 2 >= len(tokens) or tokens[idx_perim+1] != "=":
        raise check50.Mismatch("Output format: 'Perimeter = <value>'", out)
    try:
        student_perim = float(tokens[idx_perim+2])
    except ValueError:
        raise check50.Mismatch("A numeric value for Perimeter", tokens[idx_perim+2])
    expected_perim = 2.0 * 3.14 * r
    if abs(student_perim - expected_perim) > 1e-4:
        raise check50.Mismatch(f"Perimeter = {expected_perim}", f"Perimeter = {student_perim}")

@check50.check(test_compile)
def test_example():
    """handles input: 2.0"""
    out = check50.run("./circle").stdin("2.0", prompt=False).stdout()
    verify_circle_output(out, 2.0)

@check50.check(test_compile)
def test_larger():
    """handles input: 5.5"""
    out = check50.run("./circle").stdin("5.5", prompt=False).stdout()
    verify_circle_output(out, 5.5)

@check50.check(test_compile)
def test_random():
    """handles random double inputs correctly"""
    r = round(random.uniform(1.0, 50.0), 2)
    out = check50.run("./circle").stdin(f"{r:.2f}", prompt=False).stdout()
    verify_circle_output(out, r)
