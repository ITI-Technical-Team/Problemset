import check50
import re


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _html():
    return _read("index.html").lower()


# ─── existence & structure ────────────────────────────────────────────────────

@check50.check()
def exists():
    """index.html exists"""
    check50.exists("index.html")


@check50.check(exists)
def has_button():
    """index.html has a button that triggers showInfo()"""
    html = _html()
    if "<button" not in html:
        raise check50.Failure("Missing <button> element")
    if "showinfo()" not in html:
        raise check50.Failure(
            "Button does not call showInfo()",
            help="Add onclick=\"showInfo()\" to your button"
        )


# ─── JS checks ────────────────────────────────────────────────────────────────

@check50.check(exists)
def has_company_object():
    """JavaScript declares a company object with name and employees array"""
    html = _read("index.html").lower()
    
    # Check for company object declaration
    if "company" not in html:
        raise check50.Failure(
            "Missing 'company' variable",
            help="Declare a company object: let company = { ... };"
        )
    if "employees" not in html:
        raise check50.Failure(
            "company object is missing 'employees' property",
            help="company.employees must be an array of employee objects"
        )
    if "role" not in html:
        raise check50.Failure(
            "Employee objects are missing 'role' property",
            help="Each employee object inside company.employees should have a name and role property"
        )


@check50.check(exists)
def defines_showinfo_function():
    """JavaScript defines the showInfo() function"""
    html = _read("index.html")
    if "function showInfo" not in html and "const showInfo" not in html and "let showInfo" not in html:
        raise check50.Failure(
            "Missing showInfo() function",
            help="Define the function: function showInfo() { ... }"
        )


@check50.check(exists)
def showinfo_triggers_alert_and_logs():
    """showInfo() uses alert() and logs employees to the console"""
    html = _html()
    if "alert(" not in html:
        raise check50.Failure(
            "Missing alert() inside showInfo()",
            help="Use alert() to show the company name"
        )
    if "console.log" not in html:
        raise check50.Failure(
            "Missing console.log() calls",
            help="Loop through the employees array and log their name and role to the console"
        )
    if "length" not in html and "foreach" not in html:
        raise check50.Failure(
            "Missing loop to iterate through employees",
            help="Use a for loop or forEach() to iterate over company.employees"
        )
