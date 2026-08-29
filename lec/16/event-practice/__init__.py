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
    """index.html contains a non-empty button, text input, and script tag"""
    _check_tag_closed("index.html", "html")
    _check_tag_closed("index.html", "body")
    _check_tag_closed("index.html", "script")

    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")

    # Check for button with text
    btn = soup.find("button")
    if not btn or not btn.get_text().strip():
        raise check50.Failure(
            "Missing or empty button tag",
            help="Add a <button>Click Me</button> tag with text to index.html"
        )

    # Check for input type text
    inp = soup.find("input")
    if not inp:
        raise check50.Failure(
            "Missing input tag",
            help="Add an <input> tag to index.html"
        )

    inp_type = inp.get("type", "text").lower()
    if inp_type != "text":
        raise check50.Failure(
            "Input is not a text input",
            help="Ensure your input tag is a text input (e.g. <input type=\"text\">)"
        )

    if not soup.find("script"):
        raise check50.Failure(
            "Missing <script> tag",
            help="Add a `<script>` element containing your JavaScript code inside index.html"
        )


@check50.check(has_elements)
def checks_inline_event():
    """Button element uses an inline event listener (e.g., onclick)"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    btn = soup.find("button")

    inline_attrs = [
        "onclick", "onmouseover", "onmouseout", "onkeydown", "onkeyup",
        "onchange", "oninput", "onfocus", "onblur"
    ]
    has_inline = any(btn.has_attr(attr) for attr in inline_attrs)

    if not has_inline:
        raise check50.Failure(
            "Button does not use an inline event listener",
            help="Add an inline event listener attribute to your button (e.g. <button onclick=\"handleClick()\">)"
        )


@check50.check(checks_inline_event)
def checks_add_event_listener():
    """JavaScript uses addEventListener in active code for the text input"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    js_raw = soup.find("script").string or ""
    js_clean = _strip_js_comments(js_raw)

    if "addEventListener" not in js_clean:
        raise check50.Failure(
            "addEventListener not found in active script",
            help="Use addEventListener in active JavaScript code to listen to events on the text input (e.g. input.addEventListener('keyup', ...))"
        )

    btn = soup.find("button")
    onclick_attr = btn.get("onclick") if btn else ""

    # Execute under node VM to verify that listeners/functions exist and don't throw errors
    mock_env = r"""
let listenerAdded = false;
let funcCalled = false;

let inputMock = {
    value: "test",
    addEventListener: (evt, cb) => {
        listenerAdded = true;
        try { cb({ target: inputMock }); } catch (e) {}
    }
};

let elementMock = {
    textContent: "",
    value: "test",
    addEventListener: (evt, cb) => {
        listenerAdded = true;
        try { cb({ target: inputMock }); } catch (e) {}
    }
};

global.window = {};
global.alert = () => { funcCalled = true; };
global.console = { log: () => {}, error: () => {} };
global.document = {
    querySelector: (s) => inputMock,
    querySelectorAll: (s) => [inputMock],
    getElementById: (id) => elementMock,
    getElementsByTagName: (t) => [inputMock]
};
"""

    func_name = re.search(r'([a-zA-Z0-9_$]+)\s*\(', onclick_attr)
    call_func = f"try {{ {func_name.group(1)}(); }} catch(e) {{}}" if func_name else ""

    test_harness = f"""
{js_raw}
{call_func}
if (!listenerAdded) {{
    console.log("FAIL_NO_LISTENER");
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
        if out.startswith("FAIL_NO_LISTENER"):
            raise check50.Failure(
                "addEventListener was not called to attach an event to the input element",
                help="Call input.addEventListener('keyup', ...) or input.addEventListener('input', ...) in active script."
            )
        else:
            raise check50.Failure("JavaScript execution error", help=out or res.stderr.strip())
