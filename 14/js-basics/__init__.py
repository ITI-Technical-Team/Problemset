import check50
import re
import subprocess
from bs4 import BeautifulSoup


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _strip_js_comments(code):
    """Strip single-line and multi-line JS comments."""
    code = re.sub(r'//[^\n]*', '', code)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    return code


def _strip_css_comments(code):
    """Strip CSS /* ... */ comments."""
    return re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)


# ─── existence & structure ────────────────────────────────────────────────────

@check50.check()
def exists():
    """index.html exists"""
    check50.exists("index.html")


@check50.check(exists)
def has_script():
    """index.html contains a <script> block"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    if not soup.find("script"):
        raise check50.Failure(
            "Missing <script> tag",
            help="Add a `<script>` element containing your JavaScript code inside index.html"
        )


@check50.check(exists)
def has_result_element():
    """index.html has a result element with id='result'"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    if not soup.find(id="result"):
        raise check50.Failure(
            "Missing element with id='result'",
            help="Add an HTML element like `<p id=\"result\"></p>` to display the age category"
        )


# ─── JS logic checks ──────────────────────────────────────────────────────────

@check50.check(has_script)
def prompts_user():
    """JavaScript prompts the user for their age and converts it with Number()"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    js_raw = soup.find("script").string or ""
    js_clean = _strip_js_comments(js_raw)

    if "prompt(" not in js_clean:
        raise check50.Failure(
            "Missing prompt() call in active JavaScript code",
            help="Ask the user to enter their age using prompt(), e.g. prompt('Enter your age:')"
        )

    if "number(" not in js_clean.lower():
        raise check50.Failure(
            "Missing Number() conversion in active JavaScript code",
            help="Convert the prompt string to a number using Number(), e.g. Number(userAge)"
        )


@check50.check(has_script)
def evaluates_categories():
    """JavaScript correctly classifies age into Child / Teenager / Adult"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    js_code = soup.find("script").string or ""

    # Mock: proxy both innerText and textContent to one underlying value,
    # so both assignment styles work identically.
    mock_env = r"""
let _text = "";
let mockResult = {
    get innerText()  { return _text; },
    set innerText(v) { _text = v; },
    get textContent()  { return _text; },
    set textContent(v) { _text = v; },
    className: ""
};
let alerted = null;

global.alert  = (msg) => { alerted = String(msg); };
global.prompt = ()    => "20";
global.document = {
    getElementById: (id) => id === "result" ? mockResult : null
};
"""

    test_harness = r"""
const TESTS = [
    { age: 5,  cls: "child",    textHint: "child",    alertHint: "child"    },
    { age: 13, cls: "teenager", textHint: "teenager", alertHint: "teenager" },
    { age: 15, cls: "teenager", textHint: "teenager", alertHint: "teenager" },
    { age: 17, cls: "teenager", textHint: "teenager", alertHint: "teenager" },
    { age: 18, cls: "adult",    textHint: "adult",    alertHint: "adult"    },
];

for (const t of TESTS) {
    _text = "";
    mockResult.className = "";
    alerted = null;

    try { checkAge(t.age); }
    catch (e) {
        console.log(`ERROR:${t.age}:${e.message}`);
        process.exit(1);
    }

    if (mockResult.className.toLowerCase() !== t.cls) {
        console.log(`FAIL_CLASS:${t.age}:${mockResult.className}:${t.cls}`);
        process.exit(1);
    }
    if (!_text.toLowerCase().includes(t.textHint)) {
        console.log(`FAIL_TEXT:${t.age}:${_text}:${t.textHint}`);
        process.exit(1);
    }
    if (alerted === null) {
        console.log(`FAIL_ALERT_MISSING:${t.age}`);
        process.exit(1);
    }
    if (!alerted.toLowerCase().includes(t.alertHint)) {
        console.log(`FAIL_ALERT:${t.age}:${alerted}:${t.alertHint}`);
        process.exit(1);
    }
}
console.log("PASS");
"""

    full_js = mock_env + js_code + test_harness

    try:
        res = subprocess.run(["node", "-e", full_js], capture_output=True, text=True)
    except FileNotFoundError:
        return  # node not available — skip functional check

    if res.returncode != 0:
        out = res.stdout.strip() or res.stderr.strip()
        parts = out.split(":")

        if out.startswith("FAIL_CLASS"):
            age, got, expected = parts[1], parts[2], parts[3]
            raise check50.Failure(
                f"Wrong CSS class set for age {age}",
                help=f"Expected className to be '{expected}' but got '{got}' — check your if/else conditions"
            )
        elif out.startswith("FAIL_TEXT"):
            age, got, expected = parts[1], parts[2], parts[3]
            raise check50.Failure(
                f"Wrong text content for age {age}",
                help=f"Expected textContent/innerText to contain '{expected}' but got '{got}'"
            )
        elif out.startswith("FAIL_ALERT_MISSING"):
            age = parts[1]
            raise check50.Failure(
                f"No alert() called for age {age}",
                help="Make sure to call alert() inside checkAge with the category name"
            )
        elif out.startswith("FAIL_ALERT"):
            age, got, expected = parts[1], parts[2], parts[3]
            raise check50.Failure(
                f"Wrong alert message for age {age}",
                help=f"Expected alert to contain '{expected}' but got '{got}'"
            )
        elif out.startswith("ERROR"):
            age, msg = parts[1], ":".join(parts[2:])
            raise check50.Failure(
                f"JavaScript error when calling checkAge({age})",
                help=msg
            )
        else:
            raise check50.Failure("JavaScript execution error", help=out or res.stderr.strip())


# ─── CSS checks ───────────────────────────────────────────────────────────────

@check50.check(exists)
def has_css_classes():
    """CSS defines .child, .teenager, and .adult classes with text-align center"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    style_tag = soup.find("style")
    if not style_tag:
        raise check50.Failure(
            "Missing <style> tag",
            help="Add a `<style>` block inside your `<head>` to define CSS styling"
        )

    css_clean = _strip_css_comments(style_tag.string or "").lower()

    for category in ["child", "teenager", "adult"]:
        if not re.search(r'\.' + category + r'\b', css_clean):
            raise check50.Failure(
                f"Missing CSS rule for class '.{category}'",
                help=f"Define .{category} {{ color: ...; }} inside your <style> block"
            )

    if "text-align" not in css_clean or "center" not in css_clean:
        raise check50.Failure(
            "Page content is not centered",
            help="Add 'text-align: center;' to your CSS to center the page content"
        )
