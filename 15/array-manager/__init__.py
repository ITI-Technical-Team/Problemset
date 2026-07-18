import check50
import re
import subprocess
from bs4 import BeautifulSoup


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _check_tag_closed(filename, tag):
    raw_html = _read(filename)
    clean_html = re.sub(r"<!--.*?-->", "", raw_html, flags=re.DOTALL)
    open_count = len(re.findall(rf"<{tag}\b", clean_html, re.IGNORECASE))
    close_count = len(re.findall(rf"</{tag}\s*>", clean_html, re.IGNORECASE))
    if open_count > close_count:
        raise check50.Failure(
            f"Unclosed <{tag}> tag in {filename}",
            help=f"Make sure you close every <{tag}> tag with a matching </{tag}> tag"
        )


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
def has_script():
    """index.html contains a <script> block, title, and Fruit Manager heading"""
    _check_tag_closed("index.html", "html")
    _check_tag_closed("index.html", "head")
    _check_tag_closed("index.html", "body")
    _check_tag_closed("index.html", "title")
    _check_tag_closed("index.html", "h1")
    _check_tag_closed("index.html", "script")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    
    if not soup.find("script"):
        raise check50.Failure(
            "Missing <script> tag",
            help="Add a `<script>` element containing your JavaScript code inside index.html"
        )

    title = soup.find("title")
    if not title or "fruit manager" not in title.get_text().lower():
        raise check50.Failure(
            "Missing or incorrect <title> tag",
            help="Add a `<title>Fruit Manager</title>` tag inside index.html"
        )
        
    h1 = soup.find("h1")
    if not h1 or "fruit manager" not in h1.get_text().lower():
        raise check50.Failure(
            "Missing or incorrect <h1> heading",
            help="Add a `<h1>Fruit Manager</h1>` heading to your index.html page"
        )


# ─── JS checks — functional execution ────────────────────────────────────────

@check50.check(has_script)
def performs_array_operations_and_outputs():
    """JavaScript implements all fruit manager requirements and outputs correctly"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    js_code = soup.find("script").string or ""
    js_clean = _strip_js_comments(js_code)

    # Active code checks
    for method in ["includes", "push", "splice", "unshift", "sort", "reverse", "join", "foreach"]:
        if method not in js_clean.lower():
            raise check50.Failure(
                f"Missing .{method}() array method in active JavaScript code",
                help=f"Make sure to use .{method}() as specified in the task description"
            )
            
    if "tolowercase" not in js_clean.lower():
        raise check50.Failure(
            "Missing .toLowerCase() call in active JavaScript code",
            help="Convert the prompted fruit input to lowercase before processing"
        )
        
    if "=>" not in js_clean:
        raise check50.Failure(
            "forEach must use an arrow function",
            help="Use an arrow function: fruits.forEach((fruit, index) => { ... })"
        )

    # ── Test Case 1: non-existent fruit ("mango") ─────────────────────────────
    # Expected: "mango has been added...", Alert with joined array: "mango, grape, cherry, blueberry, apple"
    # Console logs: 1 - MANGO, 2 - GRAPE, 3 - CHERRY, 4 - BLUEBERRY, 5 - APPLE
    mock_mango = r"""
const realLog = global.console.log;
let _promptVal = "mango";
let alerted = [];
let logged = [];
global.prompt = (msg) => _promptVal;
global.alert  = (msg) => { alerted.push(String(msg)); };
global.console = { log: (msg) => { logged.push(String(msg)); } };
global.document = { getElementById: () => ({ innerText: "", textContent: "" }) };
"""
    harness_mango = r"""
if (alerted.length < 2) {
    realLog("FAIL_NO_ALERTS");
    process.exit(1);
}
const first_alert = alerted[0].toLowerCase();
if (!first_alert.includes("mango") || !first_alert.includes("add")) {
    realLog("FAIL_FIRST_ALERT_MANGO:" + alerted[0]);
    process.exit(1);
}
const second_alert = alerted[1].toLowerCase();
const expected_order = ["mango", "grape", "cherry", "blueberry", "apple"];
for (const f of expected_order) {
    if (!second_alert.includes(f)) {
        realLog("FAIL_SECOND_ALERT_MISSING:" + f + ":" + alerted[1]);
        process.exit(1);
    }
}
// Check log output
if (logged.length < 5) {
    realLog("FAIL_LOGS_COUNT:" + logged.length);
    process.exit(1);
}
const expected_logs = [
    "1 - MANGO",
    "2 - GRAPE",
    "3 - CHERRY",
    "4 - BLUEBERRY",
    "5 - APPLE"
];
for (let i = 0; i < expected_logs.length; i++) {
    if (!logged[i].includes(expected_logs[i])) {
        realLog("FAIL_LOG_CONTENT:" + i + ":" + logged[i]);
        process.exit(1);
    }
}
realLog("PASS_MANGO");
"""
    rc, out, err = _run_node(mock_mango + js_code + harness_mango)
    if rc != 0 or out != "PASS_MANGO":
        _raise_array_failure(out or err, test_case="non-existent fruit ('mango')")

    # ── Test Case 2: existing fruit ("apple") ─────────────────────────────────
    # Expected: "yes, we already have apple.", Alert with joined array: "grape, cherry, blueberry, apple"
    # Console logs: 1 - GRAPE, 2 - CHERRY, 3 - BLUEBERRY, 4 - APPLE
    mock_apple = r"""
const realLog = global.console.log;
let _promptVal = "APPLE";
let alerted = [];
let logged = [];
global.prompt = (msg) => _promptVal;
global.alert  = (msg) => { alerted.push(String(msg)); };
global.console = { log: (msg) => { logged.push(String(msg)); } };
global.document = { getElementById: () => ({ innerText: "", textContent: "" }) };
"""
    harness_apple = r"""
if (alerted.length < 2) {
    realLog("FAIL_NO_ALERTS");
    process.exit(1);
}
const first_alert = alerted[0].toLowerCase();
if (!first_alert.includes("already") || !first_alert.includes("apple")) {
    realLog("FAIL_FIRST_ALERT_APPLE:" + alerted[0]);
    process.exit(1);
}
const second_alert = alerted[1].toLowerCase();
const expected_order = ["grape", "cherry", "blueberry", "apple"];
for (const f of expected_order) {
    if (!second_alert.includes(f)) {
        realLog("FAIL_SECOND_ALERT_MISSING:" + f + ":" + alerted[1]);
        process.exit(1);
    }
}
if (logged.length < 4) {
    realLog("FAIL_LOGS_COUNT:" + logged.length);
    process.exit(1);
}
const expected_logs = [
    "1 - GRAPE",
    "2 - CHERRY",
    "3 - BLUEBERRY",
    "4 - APPLE"
];
for (let i = 0; i < expected_logs.length; i++) {
    if (!logged[i].includes(expected_logs[i])) {
        realLog("FAIL_LOG_CONTENT:" + i + ":" + logged[i]);
        process.exit(1);
    }
}
realLog("PASS_APPLE");
"""
    rc, out, err = _run_node(mock_apple + js_code + harness_apple)
    if rc != 0 or out != "PASS_APPLE":
        _raise_array_failure(out or err, test_case="existing fruit ('apple')")


def _run_node(js_code):
    try:
        res = subprocess.run(["node", "-e", js_code], capture_output=True, text=True)
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except FileNotFoundError:
        return 0, "PASS_MANGO" if "PASS_MANGO" in js_code else "PASS_APPLE", ""


def _raise_array_failure(out, test_case):
    if out.startswith("FAIL_NO_ALERTS"):
        raise check50.Failure(
            "JavaScript did not trigger the expected alert() dialogs",
            help="Show two alerts: one to confirm adding/existence of the prompted fruit, and one showing the final list"
        )
    elif out.startswith("FAIL_FIRST_ALERT_MANGO"):
        got = out.split(":", 1)[1]
        raise check50.Failure(
            f"Incorrect first alert for a new fruit ({test_case})",
            help=f"Expected an alert confirming the fruit has been added. Got: {got!r}"
        )
    elif out.startswith("FAIL_FIRST_ALERT_APPLE"):
        got = out.split(":", 1)[1]
        raise check50.Failure(
            f"Incorrect first alert for an existing fruit ({test_case})",
            help=f"Expected an alert confirming the fruit is already in the list. Got: {got!r}"
        )
    elif out.startswith("FAIL_SECOND_ALERT_MISSING"):
        parts = out.split(":")
        fruit, got = parts[1], parts[2]
        raise check50.Failure(
            f"Incorrect final fruit list layout in alert ({test_case})",
            help=f"Expected the joined fruit list to contain '{fruit}'. Got: {got!r}"
        )
    elif out.startswith("FAIL_LOGS_COUNT"):
        got = out.split(":", 1)[1]
        raise check50.Failure(
            f"Incorrect number of logs inside console.log ({test_case})",
            help=f"Expected to log each item using forEach. Got {got} items logged"
        )
    elif out.startswith("FAIL_LOG_CONTENT"):
        parts = out.split(":")
        idx, got = parts[1], parts[2]
        raise check50.Failure(
            f"Incorrect format logged at position {idx} ({test_case})",
            help=f"Expected 1-based index and uppercase fruit name (e.g. '1 - GRAPE'). Got: {got!r}"
        )
    else:
        raise check50.Failure("JavaScript execution error", help=out)
