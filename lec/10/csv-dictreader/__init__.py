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
    """csv-dictreader.py opens and processes favorites.csv using DictReader"""
    code = open("csv-dictreader.py", encoding="utf-8", errors="replace").read()
    
    import re
    code_clean = re.sub(r'#[^\n]*', '', code)
    
    if "DictReader" not in code_clean:
        raise check50.Failure(
            "csv-dictreader.py does not use DictReader",
            help="Make sure to use csv.DictReader(file) to read the CSV data as dictionaries"
        )
    if "open(" not in code_clean:
        raise check50.Failure(
            "csv-dictreader.py does not open favorites.csv",
            help="Use open('favorites.csv') to read the CSV file"
        )


@check50.check(test_reads_csv)
def test_output():
    """prints correct language counts dictionary"""
    # ── Test 1: standard favorites.csv ────────────────────────────────────────
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

    # ── Test 2: modified favorites.csv (appended rows to check dynamic counting)
    try:
        with open("favorites.csv", "a", encoding="utf-8") as file:
            file.write('\n"1/1/2026 12:00:00","Python","TestProblem"')
            file.write('\n"1/1/2026 12:00:00","Java","TestProblem"')
    except Exception as e:
        raise check50.Failure(f"Failed to append test rows to favorites.csv: {e}")

    result2 = check50.run("python3 csv-dictreader.py")
    result2.exit(0)
    out2 = result2.stdout().strip()
    try:
        data2 = ast.literal_eval(out2)
    except Exception:
        raise check50.Failure(
            f"Output on modified CSV is not a valid Python dictionary representation: '{out2}'",
            help="Do not print extra text or debug output"
        )
        
    if not isinstance(data2, dict):
        raise check50.Failure(f"Expected output to be a dictionary, got {type(data2).__name__}: '{out2}'")

    expected2 = {'Python': 281, 'Scratch': 40, 'C': 78, 'Java': 1}
    for k, v in expected2.items():
        if k not in data2:
            raise check50.Failure(
                f"Counts did not update dynamically. Key '{k}' not found in modified counts dictionary: '{out2}'",
                help="Make sure you read favorites.csv and count languages dynamically rather than printing a hardcoded dictionary."
            )
        if data2[k] != v:
            raise check50.Failure(
                f"Counts did not update dynamically. Expected count for '{k}' to be {v}, got {data2[k]}: '{out2}'",
                help="Make sure you read favorites.csv and count languages dynamically rather than printing a hardcoded dictionary."
            )
            
    if len(data2) != len(expected2):
        raise check50.Failure(f"Counts dictionary contains unexpected keys on modified CSV: '{out2}'")
