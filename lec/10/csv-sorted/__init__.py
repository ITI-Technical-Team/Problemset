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
    """csv-sorted.py opens and processes favorites.csv"""
    code = open("csv-sorted.py", encoding="utf-8", errors="replace").read()
    if "open(" not in code and "csv" not in code and "pandas" not in code:
        raise check50.Failure(
            "csv-sorted.py does not open or process favorites.csv",
            help="Use open('favorites.csv') or csv.DictReader to read the CSV data"
        )


@check50.check(test_python_valid)
def test_output():
    """prints language names and frequencies sorted alphabetically (A-Z)"""
    result = check50.run("python3 csv-sorted.py")
    result.exit(0)
    out = result.stdout()
    
    # Check for the key-value outputs in the string
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
