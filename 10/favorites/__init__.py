import check50
import re

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
            expected_str = str(output)
            out = super().stdout(output=None)
            if expected_str not in out:
                raise check50.Mismatch(expected_str, out)
            return self
        return super().stdout(output, *args, **kwargs)

check50.run = RobustRun


@check50.check()
def exists():
    """favorites.py exists"""
    check50.exists("favorites.py")
    check50.include("favorites.csv")


@check50.check(exists)
def test_python_valid():
    """favorites.py has no syntax errors"""
    check50.run("python3 -m py_compile favorites.py").exit(0)


@check50.check(test_python_valid)
def test_reads_csv():
    """favorites.py opens and processes favorites.csv"""
    code = open("favorites.py", encoding="utf-8", errors="replace").read()
    if "open(" not in code and "csv" not in code and "pandas" not in code:
        raise check50.Failure(
            "favorites.py does not open or process favorites.csv",
            help="Use open('favorites.csv') or csv.DictReader to read and search the CSV data"
        )


@check50.check(test_python_valid)
def test_cash():
    """counts votes for 'Cash' correctly (24)"""
    result = check50.run("python3 favorites.py").stdin("Cash", prompt=False)
    result.stdout("24", regex=False).exit(0)


@check50.check(test_python_valid)
def test_hello_world():
    """counts votes for 'Hello, World' correctly (65)"""
    result = check50.run("python3 favorites.py").stdin("Hello, World", prompt=False)
    result.stdout("65", regex=False).exit(0)


@check50.check(test_python_valid)
def test_dna():
    """counts votes for 'DNA' correctly (28)"""
    result = check50.run("python3 favorites.py").stdin("DNA", prompt=False)
    result.stdout("28", regex=False).exit(0)


@check50.check(test_python_valid)
def test_scrabble():
    """counts votes for 'Scrabble' correctly (2)"""
    result = check50.run("python3 favorites.py").stdin("Scrabble", prompt=False)
    result.stdout("2", regex=False).exit(0)


@check50.check(test_python_valid)
def test_plurality():
    """counts votes for 'Plurality' correctly (4)"""
    result = check50.run("python3 favorites.py").stdin("Plurality", prompt=False)
    result.stdout("4", regex=False).exit(0)


@check50.check(test_python_valid)
def test_not_found():
    """handles a problem that doesn't exist in data"""
    result = check50.run("python3 favorites.py").stdin("NotARealProblem", prompt=False)
    result.exit(0)
    out = result.stdout()
    if "traceback" in out.lower() or "error" in out.lower():
        raise check50.Failure(
            "Program crashed with an error on unhandled problem search",
            help="Ensure your program handles missing CSV files or missing search terms gracefully without crashing"
        )
    out_lower = out.lower()
    if "0" not in out and "not" not in out_lower and "no" not in out_lower:
        raise check50.Failure(
            "Expected either '0 votes' or a message indicating the problem is not found",
            help="Return 0 or print a not-found message when the problem doesn't exist"
        )


@check50.check(test_python_valid)
def test_case_sensitive():
    """search is case-sensitive ('cash' != 'Cash')"""
    result = check50.run("python3 favorites.py").stdin("cash", prompt=False)
    result.exit(0)
    out = result.stdout()
    if "traceback" in out.lower() or "error" in out.lower():
        raise check50.Failure(
            "Program crashed with an error when searching for 'cash'",
            help="Ensure your program handles search queries gracefully"
        )
    if "24" in out:
        raise check50.Failure(
            "Search should be case-sensitive: 'cash' is not the same as 'Cash'",
            help="Use exact string matching, not case-insensitive matching"
        )


@check50.check(test_reads_csv)
def test_dynamic_csv():
    """searches modified CSV dataset dynamically"""
    with open("favorites.csv", "w", encoding="utf-8") as f:
        f.write("Timestamp,language,problem\n")
        f.write("1/1/2025,Python,SuperMario\n")
        f.write("1/1/2025,Python,SuperMario\n")
        f.write("1/1/2025,Python,SuperMario\n")

    result = check50.run("python3 favorites.py").stdin("SuperMario", prompt=False)
    result.exit(0)
    out = result.stdout()
    if "3" not in out:
        raise check50.Failure(
            "Program did not output vote count (3) for 'SuperMario' from modified favorites.csv",
            help="Read and search favorites.csv dynamically using open() and csv library rather than hardcoding results"
        )
