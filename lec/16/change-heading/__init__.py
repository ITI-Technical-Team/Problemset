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


# ─── existence & structure ────────────────────────────────────────────────────

@check50.check()
def exists():
    """index.html exists"""
    check50.exists("index.html")


@check50.check(exists)
def has_elements():
    """index.html contains a heading, a button, and a script tag"""
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
            help="Add a heading tag like <h1>Original Heading</h1> to index.html"
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
def checks_query_selector():
    """JavaScript code uses querySelector to select the heading"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    js_raw = soup.find("script").string or ""

    if "querySelector" not in js_raw:
        raise check50.Failure(
            "querySelector not found in script",
            help="Ensure you select your heading using document.querySelector()"
        )


@check50.check(checks_query_selector)
def checks_button_click():
    """Button click updates heading text content"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    js_raw = soup.find("script").string or ""
    button = soup.find("button")
    onclick_attr = button.get("onclick") if button else None

    mock_env = r"""
let registeredClick = null;
let headingText = "Original";
let headingMock = {
    get textContent() { return headingText; },
    set textContent(v) { headingText = v; },
    get innerText() { return headingText; },
    set innerText(v) { headingText = v; },
    get innerHTML() { return headingText; },
    set innerHTML(v) { headingText = v; }
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
    querySelector: (selector) => {
        if (selector === "button" || selector.includes("btn") || selector.includes("change")) return buttonMock;
        return headingMock;
    },
    getElementById: (id) => {
        if (id.toLowerCase().includes("btn") || id.toLowerCase().includes("button")) return buttonMock;
        return headingMock;
    }
};
"""

    if onclick_attr:
        test_harness = f"""
{js_raw}
try {{
    {onclick_attr.strip()};
}} catch (e) {{
    console.log("ERROR_CLICK:" + e.message);
    process.exit(1);
}}
if (headingText === "Original") {{
    console.log("FAIL_NO_CHANGE");
    process.exit(1);
}}
console.log("PASS");
"""
    else:
        test_harness = f"""
{js_raw}
if (registeredClick) {{
    registeredClick();
}} else {{
    console.log("NO_CLICK_LISTENER");
    process.exit(1);
}}
if (headingText === "Original") {{
    console.log("FAIL_NO_CHANGE");
    process.exit(1);
}}
console.log("PASS");
"""

    full_js = mock_env + test_harness
    res = subprocess.run(["node", "-e", full_js], capture_output=True, text=True)
    if res.returncode != 0:
        out = res.stdout.strip() or res.stderr.strip()
        if out.startswith("FAIL_NO_CHANGE"):
            raise check50.Failure(
                "Heading text was not modified",
                help="Make sure you change the heading's textContent inside the button click handler"
            )
        elif out.startswith("NO_CLICK_LISTENER"):
            raise check50.Failure(
                "Button click event listener not found",
                help="Make sure you attach a click handler to the button (e.g. using onclick or addEventListener)"
            )
        else:
            raise check50.Failure("JavaScript execution error", help=out or res.stderr.strip())
