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
    """index.html contains heading, paragraph with id, button with id and text, and <script> block"""
    _check_tag_closed("index.html", "html")
    _check_tag_closed("index.html", "body")
    _check_tag_closed("index.html", "script")

    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")

    # Check for non-empty heading
    heading = soup.find(re.compile(r'^h[1-6]$', re.I))
    if not heading or not heading.get_text().strip():
        raise check50.Failure(
            "Missing or empty heading tag",
            help="Add a heading tag with text like <h1>Personal Profile</h1> to index.html"
        )

    # Check for paragraph with id
    p = soup.find("p")
    if not p:
        raise check50.Failure(
            "Missing paragraph tag",
            help="Add a <p id=\"info\"></p> tag to index.html to display personal information"
        )
    if not p.get("id"):
        raise check50.Failure(
            "Paragraph tag is missing an 'id' attribute (e.g. id=\"info\")",
            help="Add id=\"info\" to your <p> tag so JavaScript can select it with document.getElementById(\"info\")"
        )

    # Check for button with id and text
    btn = soup.find("button")
    if not btn or not btn.get_text().strip():
        raise check50.Failure(
            "Missing or empty button tag",
            help="Add a <button id=\"welcome-btn\">Change Message</button> with text to index.html"
        )
    if not btn.get("id"):
        raise check50.Failure(
            "Button tag is missing an 'id' attribute (e.g. id=\"welcome-btn\")",
            help="Add id=\"welcome-btn\" to your <button> tag so JavaScript can attach a click handler"
        )

    if not soup.find("script"):
        raise check50.Failure(
            "Missing <script> tag",
            help="Add a `<script>` element containing your JavaScript code inside index.html"
        )


@check50.check(has_elements)
def checks_variables():
    """JavaScript declares AND initializes name, age, and favorite color variables"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    js_raw = soup.find("script").string or ""
    js_clean = _strip_js_comments(js_raw).lower()

    if not re.search(r'\b(let|const|var)\s+name\s*=\s*[^;\n]+', js_clean):
        raise check50.Failure(
            "Missing or uninitialized 'name' variable",
            help="Declare and initialize a variable named 'name' with a value (e.g. let name = 'Alice';)"
        )

    if not re.search(r'\b(let|const|var)\s+age\s*=\s*[^;\n]+', js_clean):
        raise check50.Failure(
            "Missing or uninitialized 'age' variable",
            help="Declare and initialize a variable named 'age' with a number (e.g. let age = 20;)"
        )

    has_color = (
        re.search(r'\b(let|const|var)\s+favoritecolor\s*=\s*[^;\n]+', js_clean) or
        re.search(r'\b(let|const|var)\s+favorite_color\s*=\s*[^;\n]+', js_clean)
    )
    if not has_color:
        raise check50.Failure(
            "Missing or uninitialized 'favoriteColor' variable",
            help="Declare and initialize a variable named 'favoriteColor' with a color string (e.g. let favoriteColor = 'Blue';)"
        )


@check50.check(checks_variables)
def test_page_load_info():
    """Page load displays personal info in paragraph"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    p = soup.find("p")
    p_id = p.get("id", "info") if p else "info"
    js_code = soup.find("script").string or ""

    mock_env = f"""
let paragraphText = "";
let paragraphMock = {{
    get textContent() {{ return paragraphText; }},
    set textContent(v) {{ paragraphText = String(v); }},
    get innerText() {{ return paragraphText; }},
    set innerText(v) {{ paragraphText = String(v); }},
    get innerHTML() {{ return paragraphText; }},
    set innerHTML(v) {{ paragraphText = String(v); }}
}};
let buttonMock = {{
    addEventListener: () => {{}},
    set onclick(cb) {{}}
}};
global.window = {{}};
global.document = {{
    getElementById: (id) => {{
        if (id === "{p_id}") return paragraphMock;
        return buttonMock;
    }},
    querySelector: (s) => (s === "p" ? paragraphMock : buttonMock)
}};
"""
    full_js = mock_env + js_code + "\nconsole.log(paragraphText);"
    try:
        res = subprocess.run(["node", "-e", full_js], capture_output=True, text=True)
    except FileNotFoundError:
        return

    out = res.stdout.strip()
    if not out:
        raise check50.Failure(
            "Paragraph is empty when the page loads",
            help="Set the paragraph's textContent to your personal info (e.g. document.getElementById('info').textContent = 'My name is ...') when the page loads."
        )


@check50.check(test_page_load_info)
def button_click_logic():
    """Button click updates paragraph text to 'Welcome to JavaScript!'"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    p = soup.find("p")
    btn = soup.find("button")
    p_id = p.get("id", "info") if p else "info"
    btn_id = btn.get("id", "welcome-btn") if btn else "welcome-btn"

    js_code = soup.find("script").string or ""
    onclick_attr = btn.get("onclick") if btn else None

    mock_env = f"""
let registeredClick = null;
let paragraphText = "";
let paragraphMock = {{
    get textContent() {{ return paragraphText; }},
    set textContent(v) {{ paragraphText = String(v); }},
    get innerText() {{ return paragraphText; }},
    set innerText(v) {{ paragraphText = String(v); }},
    get innerHTML() {{ return paragraphText; }},
    set innerHTML(v) {{ paragraphText = String(v); }}
}};
let buttonMock = {{
    addEventListener: (event, cb) => {{
        if (event === "click") registeredClick = cb;
    }},
    set onclick(cb) {{
        registeredClick = cb;
    }}
}};

global.window = {{}};
global.document = {{
    getElementById: (id) => {{
        if (id === "{p_id}") return paragraphMock;
        if (id === "{btn_id}") return buttonMock;
        return null;
    }},
    querySelector: (selector) => {{
        if (selector === "p" || selector === "#{p_id}") return paragraphMock;
        if (selector === "button" || selector === "#{btn_id}") return buttonMock;
        return null;
    }}
}};
"""

    if onclick_attr:
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
