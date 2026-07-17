import check50
import random

@check50.check()
def exists():
    """min-max.cpp exists"""
    check50.exists("min-max.cpp")

@check50.check(exists)
def test_compile():
    """min-max.cpp compiles successfully"""
    check50.run("g++ -O1 -Wall -Wextra -Werror -fsanitize=bounds -fno-sanitize-recover=bounds -D_GLIBCXX_DEBUG min-max.cpp -o min-max").exit(0)

def verify_min_max_output(out, a, b, c):
    tokens = out.split()
    
    # Verify Minimum
    if "Minimum" not in tokens:
        raise check50.Mismatch("Output containing 'Minimum = ...'", out)
    idx_min = tokens.index("Minimum")
    if idx_min + 2 >= len(tokens) or tokens[idx_min+1] != "=":
        raise check50.Mismatch("Output format: 'Minimum = <value>'", out)
    try:
        student_min = int(tokens[idx_min+2])
    except ValueError:
        raise check50.Mismatch("An integer value for Minimum", tokens[idx_min+2])
        
    expected_min = min(a, b, c)
    if student_min != expected_min:
        raise check50.Mismatch(f"Minimum = {expected_min}", f"Minimum = {student_min}")
        
    # Verify Maximum
    if "Maximum" not in tokens:
        raise check50.Mismatch("Output containing 'Maximum = ...'", out)
    idx_max = tokens.index("Maximum")
    if idx_max + 2 >= len(tokens) or tokens[idx_max+1] != "=":
        raise check50.Mismatch("Output format: 'Maximum = <value>'", out)
    try:
        student_max = int(tokens[idx_max+2])
    except ValueError:
        raise check50.Mismatch("An integer value for Maximum", tokens[idx_max+2])
        
    expected_max = max(a, b, c)
    if student_max != expected_max:
        raise check50.Mismatch(f"Maximum = {expected_max}", f"Maximum = {student_max}")

@check50.check(test_compile)
def test_example1():
    """handles input: A = 1, B = 2, C = 3"""
    out = check50.run("./min-max").stdin("1", prompt=False).stdin("2", prompt=False).stdin("3", prompt=False).stdout()
    verify_min_max_output(out, 1, 2, 3)

@check50.check(test_compile)
def test_example2():
    """handles input: A = 1, B = 1, C = 1"""
    out = check50.run("./min-max").stdin("1", prompt=False).stdin("1", prompt=False).stdin("1", prompt=False).stdout()
    verify_min_max_output(out, 1, 1, 1)

@check50.check(test_compile)
def test_example3():
    """handles input: A = 2, B = 1, C = 2"""
    out = check50.run("./min-max").stdin("2", prompt=False).stdin("1", prompt=False).stdin("2", prompt=False).stdout()
    verify_min_max_output(out, 2, 1, 2)

@check50.check(test_compile)
def test_random():
    """handles random inputs correctly"""
    a = random.randint(-1000, 1000)
    b = random.randint(-1000, 1000)
    c = random.randint(-1000, 1000)
    out = check50.run("./min-max").stdin(str(a), prompt=False).stdin(str(b), prompt=False).stdin(str(c), prompt=False).stdout()
    verify_min_max_output(out, a, b, c)
