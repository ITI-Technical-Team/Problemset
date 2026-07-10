import check50


@check50.check()
def exists():
    """language-count.py exists"""
    check50.exists("language-count.py")
    check50.include("favorites.csv")


@check50.check(exists)
def test_python_valid():
    """language-count.py has no syntax errors"""
    check50.run("python3 -m py_compile language-count.py").exit(0)


@check50.check(test_python_valid)
def test_python_in_output():
    """output contains 'Python: 280'"""
    result = check50.run("python3 language-count.py")
    out = result.stdout()
    if "Python: 280" not in out and "Python:280" not in out:
        raise check50.Failure(
            "Expected 'Python: 280' in output",
            help="Count each value in the 'language' column and print 'Language: count'"
        )


@check50.check(test_python_valid)
def test_c_in_output():
    """output contains 'C: 78'"""
    result = check50.run("python3 language-count.py")
    out = result.stdout()
    if "C: 78" not in out and "C:78" not in out:
        raise check50.Failure(
            "Expected 'C: 78' in output",
            help="Make sure you count all languages in the 'language' column"
        )


@check50.check(test_python_valid)
def test_scratch_in_output():
    """output contains 'Scratch: 40'"""
    result = check50.run("python3 language-count.py")
    out = result.stdout()
    if "Scratch: 40" not in out and "Scratch:40" not in out:
        raise check50.Failure(
            "Expected 'Scratch: 40' in output",
            help="Make sure you count all languages, not just some of them"
        )


@check50.check(test_python_valid)
def test_descending_order():
    """languages are printed in descending order of frequency"""
    result = check50.run("python3 language-count.py")
    out = result.stdout().strip()
    lines = [l.strip() for l in out.splitlines() if l.strip()]
    # Extract counts from lines
    counts = []
    for line in lines:
        parts = line.split(":")
        if len(parts) == 2:
            try:
                counts.append(int(parts[1].strip()))
            except ValueError:
                pass
    if not counts:
        raise check50.Failure(
            "Could not parse output — expected format 'Language: count' per line"
        )
    if counts != sorted(counts, reverse=True):
        raise check50.Failure(
            f"Languages should be in descending order of frequency, but got counts: {counts}",
            help="Sort by count from highest to lowest before printing"
        )


@check50.check(test_python_valid)
def test_python_is_first():
    """Python (most popular) is printed first"""
    result = check50.run("python3 language-count.py")
    out = result.stdout().strip()
    first_line = out.splitlines()[0].strip() if out.splitlines() else ""
    if "Python" not in first_line:
        raise check50.Failure(
            f"Python should be first (it has the most votes: 280), but first line was: '{first_line}'",
            help="Sort from highest to lowest frequency"
        )
