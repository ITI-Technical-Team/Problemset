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
def has_elements():
    """index.html contains heading, paragraph, button, and <script> block"""
    _check_tag_closed("index.html", "html")
    _check_tag_closed("index.html", "body")
    _check_tag_closed("index.html", "script")

    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")

    # Check for heading
    heading = soup.find(re.compile(r'^h[1-6]$', re.I))
    if not heading:
        raise check50.Failure(
            "Missing heading tag",
            help="Add a heading tag like <h1>Personal Info</h1> to index.html"
        )

    # Check for paragraph
    p = soup.find("p")
    if not p:
        raise check50.Failure(
            "Missing paragraph tag",
            help="Add a <p> tag to index.html to display the personal information"
        )

    # Check for button
    btn = soup.find("button")
    if not btn:
        raise check50.Failure(
            "Missing button tag",
            help="Add a <button> tag to index.html"
        )

    if not soup.find("script"):
        raise check50.Failure(
            "Missing <script> tag",
            help="Add a `<script>` element containing your JavaScript code inside index.html"
        )


@check50.check(has_elements)
def checks_variables():
    """JavaScript declares name, age, and favorite color variables"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    js_raw = soup.find("script").string or ""
    js_clean = _strip_js_comments(js_raw).lower()

    if not re.search(r'\b(let|const|var)\s+name\b', js_clean):
        raise check50.Failure(
            "Missing name variable declaration",
            help="Declare a variable named 'name' (e.g. let name = 'Alice';)"
        )

    if not re.search(r'\b(let|const|var)\s+age\b', js_clean):
        raise check50.Failure(
            "Missing age variable declaration",
            help="Declare a variable named 'age' (e.g. let age = 20;)"
        )

    if not re.search(r'\b(let|const|var)\s+favoritecolor\b', js_clean) and not re.search(r'\b(let|const|var)\s+favorite_color\b', js_clean):
        raise check50.Failure(
            "Missing favoriteColor variable declaration",
            help="Declare a variable named 'favoriteColor' or 'favorite_color'"
        )


@check50.check(checks_variables)
def button_click_logic():
    """Button click updates paragraph text to 'Welcome to JavaScript!'"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    js_code = soup.find("script").string or ""
    button = soup.find("button")
    onclick_attr = button.get("onclick") if button else None

    mock_env = r"""
let registeredClick = null;
let paragraphText = "";
let paragraphMock = {
    get textContent() { return paragraphText; },
    set textContent(v) { paragraphText = v; },
    get innerText() { return paragraphText; },
    set innerText(v) { paragraphText = v; },
    get innerHTML() { return paragraphText; },
    set innerHTML(v) { paragraphText = v; }
};
let buttonMock = {
    addEventListener: (event, cb) => {
        if (event === "click") registeredClick = cb;
    },
    set onclick(cb) {
        registeredClick = cb;
    }
};

global.window = {};
global.document = {
    getElementById: (id) => {
        if (id.toLowerCase().includes("info") || id.toLowerCase().includes("para") || id.toLowerCase().includes("personal")) {
            return paragraphMock;
        }
        if (id.toLowerCase().includes("btn") || id.toLowerCase().includes("button") || id.toLowerCase().includes("click") || id.toLowerCase().includes("welcome")) {
            return buttonMock;
        }
        return {
            addEventListener: (event, cb) => { if (event === "click") registeredClick = cb; },
            set onclick(cb) { registeredClick = cb; },
            get textContent() { return paragraphText; },
            set textContent(v) { paragraphText = v; },
            get innerText() { return paragraphText; },
            set innerText(v) { paragraphText = v; }
        };
    },
    querySelector: (selector) => {
        if (selector === "p") return paragraphMock;
        if (selector === "button") return buttonMock;
        return paragraphMock;
    }
};
"""

    if onclick_attr:
        # If they used inline onclick, e.g. onclick="myFunc()"
        func_call = onclick_attr.strip()
        test_harness = f"""
{js_code}
try {{
    {func_call};
}} catch (e) {{
    console.log("ERROR_CLICK:" + e.message);
    process.exit(1);
}}
if (!paragraphText.toLowerCase().includes("welcome to javascript")) {{
    console.log("FAIL_TEXT:" + paragraphText);
    process.exit(1);
}}
console.log("PASS");
"""
    else:
        test_harness = f"""
{js_code}
if (registeredClick) {{
    registeredClick();
}} else {{
    // Try to trigger a click on document button elements directly if registered manually
    console.log("NO_CLICK_LISTENER");
    process.exit(1);
}}
if (!paragraphText.toLowerCase().includes("welcome to javascript")) {{
    console.log("FAIL_TEXT:" + paragraphText);
    process.exit(1);
}}
console.log("PASS");
"""

    full_js = mock_env + test_harness

    try:
        res = subprocess.run(["node", "-e", full_js], capture_output=True, text=True)
    except FileNotFoundError:
        return

    if res.returncode != 0:
        out = res.stdout.strip() or res.stderr.strip()
        if out.startswith("FAIL_TEXT"):
            got = out.split(":", 1)[1]
            raise check50.Failure(
                "Wrong paragraph text after button click",
                help=f"Expected paragraph text to change to 'Welcome to JavaScript!' but got '{got}'"
            )
        elif out.startswith("NO_CLICK_LISTENER"):
            raise check50.Failure(
                "Button click event listener not found",
                help="Make sure you attach a click handler to the button (e.g. using onclick or addEventListener)"
            )
        else:
            raise check50.Failure("JavaScript execution error", help=out or res.stderr.strip())
