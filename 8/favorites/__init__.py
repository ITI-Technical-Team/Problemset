import check50
import subprocess


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
def test_not_found():
    """handles a problem that doesn't exist in data"""
    result = check50.run("python3 favorites.py").stdin("NotARealProblem", prompt=False)
    out = result.stdout()
    if "0" not in out and "not" not in out.lower() and "no" not in out.lower():
        raise check50.Failure(
            "Expected either '0 votes' or a message indicating the problem is not found",
            help="Return 0 or print a not-found message when the problem doesn't exist"
        )


@check50.check(test_python_valid)
def test_case_sensitive():
    """search is case-sensitive ('cash' != 'Cash')"""
    result = check50.run("python3 favorites.py").stdin("cash", prompt=False)
    out = result.stdout()
    # cash (lowercase) should return 0 votes (or not found), NOT 24
    if "24" in out:
        raise check50.Failure(
            "Search should be case-sensitive: 'cash' is not the same as 'Cash'",
            help="Use exact string matching, not case-insensitive matching"
        )
