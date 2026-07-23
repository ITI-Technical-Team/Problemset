import check50
import ast

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
    """csv-dictreader.py exists"""
    check50.exists("csv-dictreader.py")
    check50.include("favorites.csv")


@check50.check(exists)
def test_python_valid():
    """csv-dictreader.py has no syntax errors"""
    check50.run("python3 -m py_compile csv-dictreader.py").exit(0)


@check50.check(test_python_valid)
def test_reads_csv():
    """csv-dictreader.py opens and processes favorites.csv"""
    code = open("csv-dictreader.py", encoding="utf-8", errors="replace").read()
    if "open(" not in code and "csv" not in code and "pandas" not in code:
        raise check50.Failure(
            "csv-dictreader.py does not open or process favorites.csv",
            help="Use open('favorites.csv') or csv.DictReader to read the CSV data"
        )


@check50.check(test_python_valid)
def test_output():
    """prints correct language counts dictionary"""
    result = check50.run("python3 csv-dictreader.py")
    result.exit(0)
    out = result.stdout().strip()
    try:
        data = ast.literal_eval(out)
    except Exception:
        raise check50.Failure(
            f"Output is not a valid Python literal representation: '{out}'",
            help="Ensure your script prints only the counts dictionary at the end"
        )
    
    if not isinstance(data, dict):
        raise check50.Failure(
            f"Expected output to be a dictionary, got {type(data).__name__}: '{out}'"
        )
        
    expected = {'Python': 280, 'Scratch': 40, 'C': 78}
    for k, v in expected.items():
        if k not in data:
            raise check50.Failure(f"Key '{k}' not found in counts dictionary: '{out}'")
        if data[k] != v:
            raise check50.Failure(f"Expected count for '{k}' to be {v}, got {data[k]}: '{out}'")
            
    if len(data) != len(expected):
        raise check50.Failure(f"Counts dictionary contains unexpected keys: '{out}'")
