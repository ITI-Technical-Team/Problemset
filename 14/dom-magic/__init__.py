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


def _strip_css_comments(code):
    return re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)


def _run_node(js_code):
    """Run js_code in node, return (returncode, stdout, stderr)."""
    try:
        res = subprocess.run(["node", "-e", js_code], capture_output=True, text=True)
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except FileNotFoundError:
        return 0, "PASS", ""  # node not available — skip


# ─── existence & structure ────────────────────────────────────────────────────

@check50.check()
def exists():
    """index.html exists"""
    check50.exists("index.html")


@check50.check(exists)
def has_script():
    """index.html contains a <script> block"""
    soup = BeautifulSoup(_read("index.html"), "html.parser")
    if not soup.find("script"):
        raise check50.Failure(
            "Missing <script> tag",
            help="Add a `<script>` element containing your JavaScript code inside index.html"
        )


# ─── JS checks — functional execution ────────────────────────────────────────

@check50.check(has_script)
def collects_inputs():
    """JavaScript prompts for student name and 3 subject grades"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    js_clean = _strip_js_comments(soup.find("script").string or "")

    prompts = re.findall(r'prompt\s*\(', js_clean)
    if len(prompts) < 4:
        raise check50.Failure(
            f"Found {len(prompts)} prompt(s) in active code, expected at least 4",
            help="Prompt the user for: Name, Grade 1, Grade 2, and Grade 3"
        )


@check50.check(has_script)
def calculates_and_outputs_correctly():
    """JavaScript computes correct total, toFixed(2) average, and Pass/Fail result"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    js_code = soup.find("script").string or ""

    # ── Test Case 1: passing student ──────────────────────────────────────────
    # Name="Alice", grades=60,70,80 → total=210, average=70.00, result="Pass"
    mock_passing = r"""
let _prompts = ["Alice", "60", "70", "80"];
let _pi = 0;
let _alerted = null;
global.prompt = () => _prompts[_pi++] || "0";
global.alert  = (msg) => { _alerted = String(msg); };
global.document = { getElementById: () => ({ innerText: "", textContent: "" }) };
"""
    harness_passing = r"""
if (_alerted === null) {
    console.log("FAIL_NO_ALERT");
    process.exit(1);
}
const out = _alerted.toLowerCase();
if (!out.includes("alice")) {
    console.log("FAIL_NAME:" + _alerted);
    process.exit(1);
}
if (!out.includes("210")) {
    console.log("FAIL_TOTAL:" + _alerted);
    process.exit(1);
}
if (!out.includes("70.00")) {
    console.log("FAIL_AVERAGE:" + _alerted);
    process.exit(1);
}
if (!out.includes("pass")) {
    console.log("FAIL_RESULT_PASS:" + _alerted);
    process.exit(1);
}
console.log("PASS1");
"""
    rc, out, err = _run_node(mock_passing + js_code + harness_passing)
    if rc != 0 or out != "PASS1":
        _raise_dom_failure(out or err, test_case="passing student (Alice, 60, 70, 80)")

    # ── Test Case 2: boundary pass student ───────────────────────────────────
    # Name="Bob", grades=50,50,50 → total=150, average=50.00, result="Pass" (boundary at exactly 50)
    mock_failing = r"""
let _prompts = ["Bob", "50", "50", "50"];
let _pi = 0;
let _alerted = null;
global.prompt = () => _prompts[_pi++] || "0";
global.alert  = (msg) => { _alerted = String(msg); };
global.document = { getElementById: () => ({ innerText: "", textContent: "" }) };
"""
    harness_failing = r"""
if (_alerted === null) {
    console.log("FAIL_NO_ALERT");
    process.exit(1);
}
const out2 = _alerted.toLowerCase();
if (!out2.includes("150")) {
    console.log("FAIL_TOTAL:" + _alerted);
    process.exit(1);
}
if (!out2.includes("50.00")) {
    console.log("FAIL_AVERAGE:" + _alerted);
    process.exit(1);
}
if (!out2.includes("pass")) {
    console.log("FAIL_RESULT_PASS:" + _alerted);
    process.exit(1);
}
console.log("PASS2");
"""
    rc, out, err = _run_node(mock_failing + js_code + harness_failing)
    if rc != 0 or out != "PASS2":
        _raise_dom_failure(out or err, test_case="boundary pass student (Bob, 50, 50, 50) — average exactly 50 must be 'Pass'")


def _raise_dom_failure(out, test_case):
    if out.startswith("FAIL_NO_ALERT"):
        raise check50.Failure(
            "JavaScript did not call alert() to output the student card",
            help="Use alert() at the end of your script to display all student details"
        )
    elif out.startswith("FAIL_NAME"):
        got = out.split(":", 1)[1]
        raise check50.Failure(
            "Student name is not shown in the alert output",
            help=f"Include the student's name in your alert message. Got: {got!r}"
        )
    elif out.startswith("FAIL_TOTAL"):
        got = out.split(":", 1)[1]
        raise check50.Failure(
            f"Incorrect total in the alert output ({test_case})",
            help=f"Make sure to add all 3 grades and include the total in the alert. Got: {got!r}"
        )
    elif out.startswith("FAIL_AVERAGE"):
        got = out.split(":", 1)[1]
        raise check50.Failure(
            f"Average is missing or not formatted to 2 decimal places ({test_case})",
            help=f"Divide the total by 3 and format it with .toFixed(2). Got: {got!r}"
        )
    elif out.startswith("FAIL_RESULT_PASS"):
        got = out.split(":", 1)[1]
        raise check50.Failure(
            f"Expected result 'Pass' for average >= 50, but it was not shown ({test_case})",
            help=f"Check your pass/fail threshold — use average >= 50. Got: {got!r}"
        )
    elif out.startswith("FAIL_RESULT_FAIL"):
        got = out.split(":", 1)[1]
        raise check50.Failure(
            f"Expected result 'Fail' for average < 50, but it was not shown ({test_case})",
            help=f"Check your pass/fail threshold — use average >= 50, else Fail. Got: {got!r}"
        )
    else:
        raise check50.Failure("JavaScript execution error", help=out)


# ─── CSS checks ───────────────────────────────────────────────────────────────

@check50.check(exists)
def checks_css_styling():
    """CSS centers content and applies a color to the h1 heading"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    style_tag = soup.find("style")
    if not style_tag:
        raise check50.Failure(
            "Missing <style> tag",
            help="Add a `<style>` block inside your `<head>` to define CSS styling"
        )

    css = _strip_css_comments(style_tag.string or "").lower()

    if not soup.find("h1"):
        raise check50.Failure(
            "Missing <h1> heading element",
            help="Add an <h1> heading to your page"
        )
    if "text-align" not in css or "center" not in css:
        raise check50.Failure(
            "Page content is not centered",
            help="Add 'text-align: center;' to your CSS"
        )
    if "color" not in css:
        raise check50.Failure(
            "Page heading is missing a custom color",
            help="Add color: darkred; (or any color) to your h1 or body CSS rule"
        )
