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
    """csv-reader.py exists"""
    check50.exists("csv-reader.py")
    check50.include("favorites.csv")


@check50.check(exists)
def test_python_valid():
    """csv-reader.py has no syntax errors"""
    check50.run("python3 -m py_compile csv-reader.py").exit(0)


@check50.check(test_python_valid)
def test_reads_csv():
    """csv-reader.py opens and processes favorites.csv"""
    code = open("csv-reader.py", encoding="utf-8", errors="replace").read()
    if "open(" not in code and "csv" not in code and "pandas" not in code:
        raise check50.Failure(
            "csv-reader.py does not open or process favorites.csv",
            help="Use open('favorites.csv') or csv.reader to read the CSV data"
        )


@check50.check(test_python_valid)
def test_output():
    """prints correct problem columns in order"""
    result = check50.run("python3 csv-reader.py")
    result.exit(0)
    out = result.stdout()
    lines = [line.strip().strip('"').strip("'") for line in out.splitlines() if line.strip()]
    if len(lines) < 398:
        raise check50.Failure(f"Expected 398 rows of output, but got {len(lines)}")
    expected = ["Hello, World", "DNA", "Hello, World", "Scratch", "Speller"]
    for i in range(5):
        if lines[i] != expected[i]:
            raise check50.Failure(f"Row {i+1} mismatch: expected '{expected[i]}', got '{lines[i]}'")
