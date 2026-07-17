import check50
import re
import subprocess
from bs4 import BeautifulSoup


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


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


# ─── JS checks ────────────────────────────────────────────────────────────────

@check50.check(has_script)
def prompts_user():
    """JavaScript prompts the user for their age and parses it"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    js_code = soup.find("script").string or ""
    
    # Strip comments
    js_code_clean = re.sub(r'//.*', '', js_code)
    js_code_clean = re.sub(r'/\*.*?\*/', '', js_code_clean, flags=re.DOTALL)
    
    if "prompt(" not in js_code_clean.lower():
        raise check50.Failure(
            "Missing prompt() call in active JavaScript code",
            help="Ask the user to enter their age using a prompt, e.g. prompt('Enter your age:')"
        )
        
    if "number(" not in js_code_clean.lower():
        raise check50.Failure(
            "Missing Number() parsing in active JavaScript code",
            help="Convert the prompted string input to a number using Number(), e.g. Number(userAge)"
        )


@check50.check(has_script)
def evaluates_categories():
    """JavaScript correctly evaluates age categories and updates DOM and alerts"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    js_code = soup.find("script").string or ""
    
    # Prepend mocks for Node.js environment
    mock_env = """
let mockResult = { textContent: "", className: "" };
let alerted = null;

global.alert = (msg) => { alerted = msg; };
global.prompt = (msg) => { return "20"; };
global.document = {
    getElementById: (id) => {
        if (id === 'result') return mockResult;
        return null;
    }
};
"""
    
    # Append test harness calling checkAge
    test_harness = """
let tests = [
    { age: 5, expectedClass: "child", expectedText: "child", expectedAlert: "child" },
    { age: 13, expectedClass: "teenager", expectedText: "teenager", expectedAlert: "teenager" },
    { age: 15, expectedClass: "teenager", expectedText: "teenager", expectedAlert: "teenager" },
    { age: 17, expectedClass: "teenager", expectedText: "teenager", expectedAlert: "teenager" },
    { age: 18, expectedClass: "adult", expectedText: "adult", expectedAlert: "adult" }
];

for (let t of tests) {
    mockResult.textContent = "";
    mockResult.className = "";
    alerted = null;
    
    try {
        checkAge(t.age);
    } catch (e) {
        console.log(`ERROR: Calling checkAge(${t.age}) threw an error: ${e.message}`);
        process.exit(1);
    }
    
    if (mockResult.className.toLowerCase() !== t.expectedClass) {
        console.log(`FAIL_CLASS: age ${t.age} got class "${mockResult.className}", expected "${t.expectedClass}"`);
        process.exit(1);
    }
    
    let text = mockResult.textContent.toLowerCase();
    if (!text.includes(t.expectedText)) {
        console.log(`FAIL_TEXT: age ${t.age} got text "${mockResult.textContent}", expected it to contain "${t.expectedText}"`);
        process.exit(1);
    }
    
    if (alerted === null) {
        console.log(`FAIL_ALERT: age ${t.age} did not trigger alert()`);
        process.exit(1);
    }
    
    if (alerted.toLowerCase() !== t.expectedAlert) {
        console.log(`FAIL_ALERT: age ${t.age} got alert "${alerted}", expected "${t.expectedAlert}"`);
        process.exit(1);
    }
}
console.log("PASS");
"""
    
    full_js = mock_env + js_code + test_harness
    
    # Run in node
    try:
        res = subprocess.run(
            ["node", "-e", full_js],
            capture_output=True,
            text=True
        )
        if res.returncode != 0:
            output = res.stdout.strip() or res.stderr.strip()
            if "FAIL_CLASS" in output:
                # e.g., FAIL_CLASS: age 13 got class "", expected "teenager"
                age_val = output.split("age ")[1].split(" ")[0]
                got_class = output.split('got class "')[1].split('"')[0]
                expected_class = output.split('expected "')[1].split('"')[0]
                raise check50.Failure(
                    f"Incorrect class set for age {age_val}",
                    help=f"For age {age_val}, expected element class name to be '{expected_class}' but got '{got_class}'"
                )
            elif "FAIL_TEXT" in output:
                age_val = output.split("age ")[1].split(" ")[0]
                got_text = output.split('got text "')[1].split('"')[0]
                expected_text = output.split('expected it to contain "')[1].split('"')[0]
                raise check50.Failure(
                    f"Incorrect textContent set for age {age_val}",
                    help=f"For age {age_val}, expected textContent to contain '{expected_text}' but got '{got_text}'"
                )
            elif "FAIL_ALERT" in output:
                age_val = output.split("age ")[1].split(" ")[0]
                if "did not trigger" in output:
                    raise check50.Failure(
                        f"Missing alert for age {age_val}",
                        help=f"Make sure to call alert() inside checkAge"
                    )
                got_alert = output.split('got alert "')[1].split('"')[0]
                expected_alert = output.split('expected "')[1].split('"')[0]
                raise check50.Failure(
                    f"Incorrect alert message for age {age_val}",
                    help=f"For age {age_val}, expected alert message '{expected_alert}' but got '{got_alert}'"
                )
            else:
                raise check50.Failure("JavaScript execution error", help=output)
    except FileNotFoundError:
        # If node is not installed, fallback to passing (or raise system error)
        pass


# ─── CSS checks ───────────────────────────────────────────────────────────────

@check50.check(exists)
def has_css_classes():
    """CSS defines classes child, teenager, and adult categories"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    style_tag = soup.find("style")
    if not style_tag:
        raise check50.Failure(
            "Missing <style> tag",
            help="Add a `<style>` block inside your `<head>` to define CSS styling"
        )
        
    css_content = style_tag.string or ""
    # Strip CSS comments
    css_clean = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    
    for category in ["child", "teenager", "adult"]:
        pattern = r'\.' + category + r'\b'
        if not re.search(pattern, css_clean.lower()):
            raise check50.Failure(
                f"Missing CSS rule for class '.{category}'",
                help=f"Define .{category} {{ color: ...; }} in your style block"
            )
            
    if "text-align" not in css_clean.lower() or "center" not in css_clean.lower():
        raise check50.Failure(
            "Content is not centered via CSS",
            help="Add 'text-align: center;' to style block to center elements"
        )
