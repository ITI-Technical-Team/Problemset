import check50
import re
import subprocess
from bs4 import BeautifulSoup


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _strip_js_comments(code):
    code = re.sub(r'//[^\n]*', '', code)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    return code


# ─── existence & structure ────────────────────────────────────────────────────

@check50.check()
def exists():
    """index.html exists"""
    check50.exists("index.html")


@check50.check(exists)
def has_title():
    """index.html has page title 'Company Info - Objects Task'"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("title")
    if not title:
        raise check50.Failure("Missing <title> element")
    text = title.get_text().strip()
    if text != "Company Info - Objects Task":
        raise check50.Failure(
            f"Expected page title to be 'Company Info - Objects Task', but found '{text}'",
            help="Add <title>Company Info - Objects Task</title> inside the <head> block"
        )


@check50.check(exists)
def has_heading():
    """index.html has heading 'Object Task: Company Info'"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    if not h1:
        raise check50.Failure("Missing <h1> element")
    text = h1.get_text().strip()
    if text != "Object Task: Company Info":
        raise check50.Failure(
            f"Expected <h1> heading to be 'Object Task: Company Info', but found '{text}'",
            help="Add <h1>Object Task: Company Info</h1> to your page body"
        )


@check50.check(exists)
def has_button():
    """index.html has a button that triggers showInfo()"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    btn = soup.find("button")
    if not btn:
        raise check50.Failure("Missing <button> element")
        
    onclick = btn.get("onclick", "")
    if "showinfo()" not in onclick.lower().replace(" ", ""):
        raise check50.Failure(
            "Button does not call showInfo() on click",
            help="Add onclick=\"showInfo()\" to your button"
        )


# ─── JS checks — functional execution ────────────────────────────────────────

@check50.check(has_button)
def verifies_company_and_showinfo():
    """JavaScript defines company object and showInfo() function correctly"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script")
    if not script:
        raise check50.Failure("Missing <script> tag")
        
    js_code = script.string or ""
    js_clean = _strip_js_comments(js_code)

    # Simple active code checks for function definition
    if "showinfo" not in js_clean.lower():
         raise check50.Failure(
            "Missing showInfo() function",
            help="Define the function: function showInfo() { ... }"
        )

    # Node environment setup to validate structure and output
    mock_env = r"""
const realLog = global.console.log;
let alerted = null;
let logged = [];
global.alert  = (msg) => { alerted = String(msg); };
global.console = { log: (msg) => { logged.push(String(msg)); } };
global.document = { getElementById: () => ({ innerText: "", textContent: "" }) };
"""

    test_harness = r"""
// 1. Verify company object exists and is styled correctly
if (typeof company === "undefined") {
    realLog("FAIL_NO_COMPANY");
    process.exit(1);
}
if (typeof company !== "object" || company === null) {
    realLog("FAIL_COMPANY_TYPE");
    process.exit(1);
}
if (!company.name || typeof company.name !== "string") {
    realLog("FAIL_COMPANY_NAME");
    process.exit(1);
}
if (!Array.isArray(company.employees)) {
    realLog("FAIL_NO_EMPLOYEES");
    process.exit(1);
}
if (company.employees.length === 0) {
    realLog("FAIL_EMPTY_EMPLOYEES");
    process.exit(1);
}
for (const emp of company.employees) {
    if (!emp.name || !emp.role) {
        realLog("FAIL_EMPLOYEE_FIELDS");
        process.exit(1);
    }
}

// 2. Verify showInfo function exists
if (typeof showInfo !== "function") {
    realLog("FAIL_NO_SHOWINFO");
    process.exit(1);
}

// 3. Test execution of showInfo()
try {
    showInfo();
} catch (e) {
    realLog("ERROR:" + e.message);
    process.exit(1);
}

if (alerted === null) {
    realLog("FAIL_NO_ALERT");
    process.exit(1);
}
if (!alerted.toLowerCase().includes(company.name.toLowerCase())) {
    realLog("FAIL_ALERT_TEXT:" + alerted);
    process.exit(1);
}
if (logged.length < 2) {
    realLog("FAIL_LOGS_COUNT:" + logged.length);
    process.exit(1);
}

// Verify that logged entries mention each employee and their role
for (const emp of company.employees) {
    let found = false;
    for (const log of logged) {
        if (log.toLowerCase().includes(emp.name.toLowerCase()) && log.toLowerCase().includes(emp.role.toLowerCase())) {
            found = true;
            break;
        }
    }
    if (!found) {
        realLog("FAIL_LOG_MISSING_EMPLOYEE:" + emp.name);
        process.exit(1);
    }
}

realLog("PASS");
"""

    full_js = mock_env + js_code + test_harness

    try:
        res = subprocess.run(["node", "-e", full_js], capture_output=True, text=True)
    except FileNotFoundError:
        return

    if res.returncode != 0:
        out = res.stdout.strip() or res.stderr.strip()
        if out.startswith("FAIL_NO_COMPANY"):
            raise check50.Failure(
                "Missing 'company' variable",
                help="Declare a company object: let company = { name: '...', employees: [...] };"
            )
        elif out.startswith("FAIL_COMPANY_TYPE"):
            raise check50.Failure(
                "Variable 'company' should be an object",
                help="Make sure company is declared as an object: let company = { ... }"
            )
        elif out.startswith("FAIL_COMPANY_NAME"):
            raise check50.Failure(
                "company object is missing the 'name' property",
                help="Declare the company name, e.g., name: 'TechCorp'"
            )
        elif out.startswith("FAIL_NO_EMPLOYEES"):
            raise check50.Failure(
                "company object is missing 'employees' array",
                help="company.employees must be a list of employee objects"
            )
        elif out.startswith("FAIL_EMPTY_EMPLOYEES"):
            raise check50.Failure(
                "company.employees array is empty",
                help="Add at least 3 employee objects inside company.employees"
            )
        elif out.startswith("FAIL_EMPLOYEE_FIELDS"):
            raise check50.Failure(
                "Employee objects are missing required properties",
                help="Each employee object inside company.employees should have a 'name' and 'role' property"
            )
        elif out.startswith("FAIL_NO_SHOWINFO"):
            raise check50.Failure(
                "Missing showInfo() function",
                help="Define the function: function showInfo() { ... }"
            )
        elif out.startswith("FAIL_NO_ALERT"):
            raise check50.Failure(
                "showInfo() did not call alert()",
                help="Use alert() inside showInfo() to show the company name"
            )
        elif out.startswith("FAIL_ALERT_TEXT"):
            got = out.split(":", 1)[1]
            raise check50.Failure(
                "alert message does not display the company name",
                help=f"Expected alert to contain company name. Got: {got!r}"
            )
        elif out.startswith("FAIL_LOGS_COUNT"):
            raise check50.Failure(
                "Missing console.log() output",
                help="Loop through the employees array and log their name and role to the console"
            )
        elif out.startswith("FAIL_LOG_MISSING_EMPLOYEE"):
            emp_name = out.split(":", 1)[1]
            raise check50.Failure(
                f"Missing or incorrect console.log output for employee '{emp_name}'",
                help=f"Make sure to log both the name and role of '{emp_name}' using console.log()"
            )
        elif out.startswith("ERROR"):
            raise check50.Failure(
                "JavaScript error in showInfo()",
                help=out.split(":", 1)[1]
            )
        else:
            raise check50.Failure("JavaScript execution error", help=out)
