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


def _strip_css_comments(code):
    return re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)


# ─── existence & structure ────────────────────────────────────────────────────

@check50.check()
def exists():
    """index.html exists"""
    check50.exists("index.html")


@check50.check(exists)
def has_info_element():
    """index.html contains title, heading, and element with id='info'"""
    _check_tag_closed("index.html", "html")
    _check_tag_closed("index.html", "head")
    _check_tag_closed("index.html", "body")
    _check_tag_closed("index.html", "title")
    _check_tag_closed("index.html", "p")
    _check_tag_closed("index.html", "button")
    _check_tag_closed("index.html", "script")
    
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    
    # Title verification
    title = soup.find("title")
    if not title or title.get_text().strip().lower() != "greet user":
        raise check50.Failure(
            "Expected page title to be 'Greet User'",
            help="Set your <title> tag text to exactly: 'Greet User'"
        )

    if not soup.find(id="info"):
        raise check50.Failure(
            "Missing element with id='info'",
            help="Add a paragraph or div with id=\"info\" to hold the welcome message"
        )


@check50.check(exists)
def has_button_trigger():
    """index.html contains a button that calls showInfo() and is labeled 'Click Me'"""
    html = _read("index.html").lower()
    soup = BeautifulSoup(html, "html.parser")
    btn = soup.find("button")
    if not btn:
        raise check50.Failure("Missing <button> element")
        
    btn_text = btn.get_text().strip().lower()
    if "click me" not in btn_text:
        raise check50.Failure(
            "Button text should be 'Click Me'",
            help="Label your button as 'Click Me': <button onclick=\"showInfo()\">Click Me</button>"
        )
        
    onclick = (btn.get("onclick") or "").lower().replace(" ", "")
    if "showinfo()" not in onclick:
        raise check50.Failure(
            "Button does not trigger showInfo() on click",
            help="Add onclick=\"showInfo()\" to your button element"
        )



# ─── JS checks ────────────────────────────────────────────────────────────────

@check50.check(exists)
def has_showinfo_function():
    """JavaScript defines a showInfo() function"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    script_tag = soup.find("script")
    if not script_tag:
        raise check50.Failure("Missing <script> tag")
    js_clean = _strip_js_comments(script_tag.string or "")
    if "showinfo" not in js_clean.lower():
        raise check50.Failure(
            "Missing showInfo() function definition",
            help="Define your click handler: function showInfo() { ... }"
        )


@check50.check(exists)
def showinfo_prompts_and_greets():
    """showInfo() prompts for name, updates #info with greeting, and alerts"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    script_tag = soup.find("script")
    if not script_tag:
        raise check50.Failure("Missing <script> tag")

    js_code = script_tag.string or ""
    js_clean = _strip_js_comments(js_code)

    # Active-code checks
    if "prompt(" not in js_clean:
        raise check50.Failure(
            "Missing prompt() call in active JavaScript code",
            help="Ask the user for their name using prompt(), e.g. prompt('What is your name?')"
        )
    if "alert(" not in js_clean:
        raise check50.Failure(
            "Missing alert() call in active JavaScript code",
            help="Call alert() inside showInfo() to confirm the greeting was updated"
        )

    # Functional Node.js execution
    mock_env = r"""
let _infoText = "Welcome!";
let alerted = null;
let promptCalled = false;

global.prompt = (msg) => { promptCalled = true; return "TestName"; };
global.alert  = (msg) => { alerted = String(msg); };
global.document = {
    getElementById: (id) => ({
        get innerText()    { return _infoText; },
        set innerText(v)   { _infoText = v; },
        get textContent()  { return _infoText; },
        set textContent(v) { _infoText = v; },
    })
};
"""

    test_harness = r"""
try { showInfo(); }
catch (e) {
    console.log("ERROR:" + e.message);
    process.exit(1);
}

if (!promptCalled) {
    console.log("FAIL_NO_PROMPT");
    process.exit(1);
}
if (!_infoText.toLowerCase().includes("testname")) {
    console.log("FAIL_GREETING:" + _infoText);
    process.exit(1);
}
if (alerted === null) {
    console.log("FAIL_NO_ALERT");
    process.exit(1);
}
console.log("PASS");
"""

    full_js = mock_env + js_code + test_harness

    try:
        res = subprocess.run(["node", "-e", full_js], capture_output=True, text=True)
    except FileNotFoundError:
        return

    if res.returncode != 0:
        out = res.stdout.strip() or res.stderr.strip()
        if out.startswith("FAIL_NO_PROMPT"):
            raise check50.Failure(
                "showInfo() did not call prompt()",
                help="Use prompt() inside showInfo() to ask for the user's name"
            )
        elif out.startswith("FAIL_GREETING"):
            got = out.split(":", 1)[1]
            raise check50.Failure(
                "Greeting does not include the user's name",
                help=f"Expected #info to contain the name from prompt(), but got: '{got}'"
            )
        elif out.startswith("FAIL_NO_ALERT"):
            raise check50.Failure(
                "showInfo() did not call alert()",
                help="Call alert() inside showInfo() after updating the greeting"
            )
        elif out.startswith("ERROR"):
            raise check50.Failure(
                "JavaScript error in showInfo()",
                help=out.split(":", 1)[1]
            )
        else:
            raise check50.Failure("JavaScript execution error", help=out or res.stderr.strip())


# ─── CSS checks ───────────────────────────────────────────────────────────────

@check50.check(exists)
def checks_css_styling():
    """CSS centers the page and styles #info and the button"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    style_tag = soup.find("style")
    if not style_tag:
        raise check50.Failure(
            "Missing <style> tag",
            help="Add a `<style>` block inside your `<head>` to define CSS"
        )

    css = _strip_css_comments(style_tag.string or "").lower()

    if "text-align" not in css or "center" not in css:
        raise check50.Failure(
            "Page content is not centered",
            help="Add 'text-align: center;' to your CSS"
        )
    if "#info" not in css:
        raise check50.Failure(
            "Missing CSS rule for #info",
            help="Style the welcome message: #info { font-size: 22px; color: darkblue; }"
        )
    if "padding" not in css:
        raise check50.Failure(
            "Button is missing a padding property in CSS",
            help="Add padding to your button, e.g. padding: 10px 20px;"
        )
    if "background-color" not in css:
        raise check50.Failure(
            "Button is missing a background-color property in CSS",
            help="Add background-color to your button"
        )
    if "color" not in css:
        raise check50.Failure(
            "Button is missing a color property in CSS",
            help="Set the text color of the button (e.g., color: white;)"
        )
    if "border-radius" not in css:
        raise check50.Failure(
            "Button is missing a border-radius property in CSS",
            help="Add border-radius to your button for rounded corners"
        )
