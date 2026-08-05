import check50

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
    """csv-sorted.py exists"""
    check50.exists("csv-sorted.py")
    check50.include("favorites.csv")


@check50.check(exists)
def test_python_valid():
    """csv-sorted.py has no syntax errors"""
    check50.run("python3 -m py_compile csv-sorted.py").exit(0)


@check50.check(test_python_valid)
def test_reads_csv():
    """csv-sorted.py opens and processes favorites.csv using DictReader"""
    code = open("csv-sorted.py", encoding="utf-8", errors="replace").read()
    
    import re
    code_clean = re.sub(r'#[^\n]*', '', code)
    
    if "DictReader" not in code_clean:
        raise check50.Failure(
            "csv-sorted.py does not use DictReader",
            help="Make sure to use csv.DictReader(file) to read the CSV data as dictionaries"
        )
    if "open(" not in code_clean:
        raise check50.Failure(
            "csv-sorted.py does not open favorites.csv",
            help="Use open('favorites.csv') to read the CSV file"
        )


@check50.check(test_reads_csv)
def test_output():
    """prints language names and frequencies sorted alphabetically (A-Z)"""
    # ── Test 1: standard favorites.csv ────────────────────────────────────────
    result = check50.run("python3 csv-sorted.py")
    result.exit(0)
    out = result.stdout()
    
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    if len(lines) != 3:
        raise check50.Failure(
            f"Expected exactly 3 lines of output, but got {len(lines)}.",
            help="Ensure you only print the final sorted frequencies, with no duplicate or extra print statements."
        )
    
    idx_c = out.find("C: 78")
    idx_py = out.find("Python: 280")
    idx_scr = out.find("Scratch: 40")
    
    if idx_c == -1:
        raise check50.Failure("Expected count for 'C' (C: 78) not found in output")
    if idx_py == -1:
        raise check50.Failure("Expected count for 'Python' (Python: 280) not found in output")
    if idx_scr == -1:
        raise check50.Failure("Expected count for 'Scratch' (Scratch: 40) not found in output")
        
    if not (idx_c < idx_py < idx_scr):
        raise check50.Failure(
            "Output is not sorted alphabetically from A to Z",
            help="Ensure you print C first, then Python, then Scratch"
        )

    # ── Test 2: modified favorites.csv (appended rows to check dynamic sorting)
    try:
        with open("favorites.csv", "a", encoding="utf-8") as file:
            file.write('\n"1/1/2026 12:00:00","Python","TestProblem"')
            file.write('\n"1/1/2026 12:00:00","Java","TestProblem"')
    except Exception as e:
        raise check50.Failure(f"Failed to append test rows to favorites.csv: {e}")

    result2 = check50.run("python3 csv-sorted.py")
    result2.exit(0)
    out2 = result2.stdout()

    lines2 = [line.strip() for line in out2.splitlines() if line.strip()]
    if len(lines2) != 4:
        raise check50.Failure(
            f"Expected exactly 4 lines of output on modified CSV, but got {len(lines2)}.",
            help="Ensure you only print the final sorted frequencies, with no duplicate or extra print statements."
        )

    idx_c2 = out2.find("C: 78")
    idx_java2 = out2.find("Java: 1")
    idx_py2 = out2.find("Python: 281")
    idx_scr2 = out2.find("Scratch: 40")

    if idx_java2 == -1:
        raise check50.Failure(
            "Counts and sorting did not update dynamically. Expected Java to be counted and printed on modified CSV",
            help="Make sure you read favorites.csv and print language frequencies dynamically rather than printing a hardcoded list."
        )
    if idx_py2 == -1:
        raise check50.Failure(
            "Counts did not update dynamically. Expected Python count to be 281 on modified CSV",
            help="Make sure you read favorites.csv and print language frequencies dynamically rather than printing a hardcoded list."
        )
    if idx_c2 == -1:
        raise check50.Failure("Expected count for 'C' (C: 78) not found in output on modified CSV")
    if idx_scr2 == -1:
        raise check50.Failure("Expected count for 'Scratch' (Scratch: 40) not found in output on modified CSV")

    if not (idx_c2 < idx_java2 < idx_py2 < idx_scr2):
        raise check50.Failure(
            "Output is not sorted alphabetically from A to Z on modified CSV",
            help="Make sure you sort all languages alphabetically: C, then Java, then Python, then Scratch"
        )
