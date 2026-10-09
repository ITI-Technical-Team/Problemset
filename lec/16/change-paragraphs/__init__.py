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
    """index.html contains three non-empty paragraphs, a non-empty button, and a script tag"""
    _check_tag_closed("index.html", "html")
    _check_tag_closed("index.html", "body")
    _check_tag_closed("index.html", "script")

    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")

    # Check for paragraphs with text
    paras = [p for p in soup.find_all("p") if p.get_text().strip()]
    if len(paras) < 3:
        raise check50.Failure(
            f"Found {len(paras)} non-empty paragraph tag(s), expected at least 3",
            help="Add at least three <p> elements with text content to index.html"
        )

    # Check for non-empty button
    btn = soup.find("button")
    if not btn or not btn.get_text().strip():
        raise check50.Failure(
            "Missing or empty button tag",
            help="Add a <button>Change Paragraphs</button> tag with text to index.html"
        )

    if not soup.find("script"):
        raise check50.Failure(
            "Missing <script> tag",
            help="Add a `<script>` element containing your JavaScript code inside index.html"
        )


@check50.check(has_elements)
def checks_query_selector_all():
    """JavaScript code uses querySelectorAll in active code to select the paragraphs"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    js_raw = soup.find("script").string or ""
    js_clean = _strip_js_comments(js_raw)

    if "querySelectorAll" not in js_clean:
        raise check50.Failure(
            "querySelectorAll not found in active script",
            help="Ensure you select all paragraphs in active JavaScript code using document.querySelectorAll('p')"
        )


@check50.check(checks_query_selector_all)
def checks_button_click():
    """Button click updates all three paragraphs"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    js_raw = soup.find("script").string or ""
    button = soup.find("button")
    onclick_attr = button.get("onclick") if button else None

    mock_env = r"""
let registeredClick = null;
let p1Text = "Original1";
let p2Text = "Original2";
let p3Text = "Original3";

function createPMock(pIndex, getVal, setVal) {
    return {
        get textContent() { return getVal(); },
        set textContent(v) { setVal(v); },
        get innerText() { return getVal(); },
        set innerText(v) { setVal(v); },
        get innerHTML() { return getVal(); },
        set innerHTML(v) { setVal(v); }
    };
}

let p1Mock = createPMock(1, () => p1Text, (v) => p1Text = v);
let p2Mock = createPMock(2, () => p2Text, (v) => p2Text = v);
let p3Mock = createPMock(3, () => p3Text, (v) => p3Text = v);

let paragraphsArray = [p1Mock, p2Mock, p3Mock];

let paragraphsMock = {
    length: 3,
    0: p1Mock,
    1: p2Mock,
    2: p3Mock,
    forEach: (cb) => {
        paragraphsArray.forEach(cb);
    },
    [Symbol.iterator]: function* () {
        yield p1Mock;
        yield p2Mock;
        yield p3Mock;
    }
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
    querySelectorAll: (selector) => {
        if (selector === "p") return paragraphsMock;
        return paragraphsMock;
    },
    querySelector: (selector) => {
        if (selector === "button" || selector.includes("btn") || selector.includes("change")) return buttonMock;
        return p1Mock;
    },
    getElementById: (id) => {
        if (id.toLowerCase().includes("btn") || id.toLowerCase().includes("button") || id.toLowerCase().includes("change")) return buttonMock;
        return p1Mock;
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
if (p1Text === "Original1" || p2Text === "Original2" || p3Text === "Original3") {{
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
if (p1Text === "Original1" || p2Text === "Original2" || p3Text === "Original3") {{
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
                "Not all paragraphs were updated",
                help="Make sure you loop through all paragraphs and change their textContent inside the button click handler"
            )
        elif out.startswith("NO_CLICK_LISTENER"):
            raise check50.Failure(
                "Button click event listener not found",
                help="Make sure you attach a click handler to the button (e.g. using onclick or addEventListener)"
            )
        else:
            raise check50.Failure("JavaScript execution error", help=out or res.stderr.strip())
