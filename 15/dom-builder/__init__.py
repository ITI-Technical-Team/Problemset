import check50
import re
import subprocess
import os
from bs4 import BeautifulSoup


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _get_css():
    """Retrieve all CSS content from index.html style tags and style.css (if it exists)"""
    css_content = ""
    html = _read("index.html")
    style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE)
    for block in style_blocks:
        css_content += "\n" + block
    
    if os.path.exists("style.css"):
        css_content += "\n" + _read("style.css")
        
    return css_content


def _normalize_selector(sel):
    return re.sub(r'\s+', ' ', sel.strip().lower())


def _parse_css(css_text):
    """Parse CSS into a dict: {selector: {property: value}}"""
    css_clean = re.sub(r'/\*.*?\*/', '', css_text, flags=re.DOTALL)
    rules = {}
    matches = re.findall(r'([^{]+)\{([^}]+)\}', css_clean)
    for selector, body in matches:
        selectors = [_normalize_selector(s) for s in selector.split(",")]
        props = {}
        for decl in body.split(";"):
            if ":" in decl:
                p, v = decl.split(":", 1)
                props[p.strip().lower()] = v.strip().lower()
        for sel in selectors:
            if sel in rules:
                rules[sel].update(props)
            else:
                rules[sel] = props
    return rules


# ─── existence & structure ────────────────────────────────────────────────────

@check50.check()
def exists():
    """index.html exists"""
    check50.exists("index.html")


@check50.check(exists)
def has_html_structure():
    """index.html contains heading #title and 3 paragraphs with class 'info'"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    
    title = soup.find(id="title")
    if not title:
        raise check50.Failure(
            "Missing heading with id='title'",
            help="Add a heading: <h1 id=\"title\">Welcome to JavaScript!</h1>"
        )
        
    paragraphs = soup.find_all("p", class_="info")
    if len(paragraphs) != 3:
        raise check50.Failure(
            f"Found {len(paragraphs)} paragraph(s) with class 'info', expected exactly 3",
            help="Add exactly three `<p class=\"info\">` elements to the page"
        )
        
    btn = soup.find("button")
    if not btn:
         raise check50.Failure("Missing <button> element")
         
    onclick = btn.get("onclick", "")
    if "editparagraphs()" not in onclick.lower().replace(" ", ""):
         raise check50.Failure(
            "Button does not trigger editParagraphs() on click",
            help="Add onclick=\"editParagraphs()\" to your button"
        )


# ─── JS checks — functional execution ────────────────────────────────────────

@check50.check(has_html_structure)
def js_dom_selection_and_modification():
    """editParagraphs() modifies the DOM elements correctly inside Node.js"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script")
    if not script:
        raise check50.Failure("Missing <script> tag")
        
    js_code = script.string or ""
    
    # Active code method existence check
    js_clean = re.sub(r'//[^\n]*', '', js_code)
    js_clean = re.sub(r'/\*.*?\*/', '', js_clean, flags=re.DOTALL)
    
    if "queryselectorall" not in js_clean.lower():
        raise check50.Failure(
            "Missing querySelectorAll() call in active JavaScript",
            help="Use document.querySelectorAll('.info') to select all three paragraphs"
        )
        
    if "foreach" not in js_clean.lower():
        raise check50.Failure(
            "Missing .forEach() loop in active JavaScript",
            help="Use .forEach() to iterate over the selected paragraphs"
        )

    # Functional validation mock
    mock_env = r"""
let _titleVal = "Welcome to JavaScript!";
let _paras = [
    { textContent: "This is the first paragraph.", innerHTML: "This is the first paragraph." },
    { textContent: "This is the second paragraph.", innerHTML: "This is the second paragraph." },
    { textContent: "This is the third paragraph.", innerHTML: "This is the third paragraph." }
];

let mockTitle = {
    get textContent()  { return _titleVal; },
    set textContent(v) { _titleVal = v; },
    get innerHTML()    { return _titleVal; },
    set innerHTML(v)  { _titleVal = v; }
};

global.document = {
    querySelector: (sel) => {
        if (sel === "#title" || sel === "h1" || sel === "[id='title']") {
            return mockTitle;
        }
        return null;
    },
    querySelectorAll: (sel) => {
        if (sel === ".info" || sel === "p.info" || sel === "p") {
            return _paras;
        }
        return [];
    }
};
"""

    test_harness = r"""
if (typeof editParagraphs !== "function") {
    console.log("FAIL_NO_FUNCTION");
    process.exit(1);
}

try {
    editParagraphs();
} catch (e) {
    console.log("ERROR:" + e.message);
    process.exit(1);
}

// Check title update
if (!_titleVal.toLowerCase().includes("edited")) {
    console.log("FAIL_TITLE_NOT_EDITED:" + _titleVal);
    process.exit(1);
}

// Check paragraphs updates
const expected = [
    "THIS IS THE FIRST SENTENCE.",
    "THIS IS THE SECOND SENTENCE.",
    "THIS IS THE THIRD SENTENCE."
];

for (let i = 0; i < _paras.length; i++) {
    const html = _paras[i].innerHTML;
    if (!html.includes('edited') || !html.includes('<span')) {
        console.log("FAIL_SPAN_MISSING:" + i + ":" + html);
        process.exit(1);
    }
    const clean_text = html.replace(/<[^>]+>/g, '').trim();
    if (clean_text !== expected[i]) {
        console.log("FAIL_TEXT_MISMATCH:" + i + ":" + clean_text + ":" + expected[i]);
        process.exit(1);
    }
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
        if out.startswith("FAIL_NO_FUNCTION"):
            raise check50.Failure(
                "Missing editParagraphs() function",
                help="Define the function: function editParagraphs() { ... }"
            )
        elif out.startswith("FAIL_TITLE_NOT_EDITED"):
            got = out.split(":", 1)[1]
            raise check50.Failure(
                "Heading title was not appended with ' - Edited'",
                help=f"Make sure to update the heading text content. Got: {got!r}"
            )
        elif out.startswith("FAIL_SPAN_MISSING"):
            parts = out.split(":")
            idx, got = parts[1], parts[2]
            raise check50.Failure(
                f"Paragraph at index {idx} does not wrap updated text in span with class 'edited'",
                help=f"Expected paragraph's innerHTML to set `<span class=\"edited\">...</span>`. Got: {got!r}"
            )
        elif out.startswith("FAIL_TEXT_MISMATCH"):
            parts = out.split(":")
            idx, got, expected_str = parts[1], parts[2], parts[3]
            raise check50.Failure(
                f"Paragraph at index {idx} text update is incorrect",
                help=f"Expected: {expected_str!r}. Got: {got!r} — make sure to convert to uppercase and replace 'PARAGRAPH' with 'SENTENCE'"
            )
        elif out.startswith("ERROR"):
            raise check50.Failure(
                "JavaScript error in editParagraphs()",
                help=out.split(":", 1)[1]
            )
        else:
            raise check50.Failure("JavaScript execution error", help=out)


# ─── CSS checks ───────────────────────────────────────────────────────────────

@check50.check(exists)
def checks_css_styling():
    """CSS centers the page and defines '.edited' class styling"""
    css_text = _get_css()
    rules = _parse_css(css_text)
    
    # 1. Check center alignment
    has_center = False
    for sel, props in rules.items():
        if "body" in sel or "h1" in sel or "*" in sel or ".info" in sel:
            if props.get("text-align") == "center":
                has_center = True
                break
                
    if not has_center:
         raise check50.Failure(
            "Page content is not centered",
            help="Add 'text-align: center;' to your CSS rules (e.g. inside body { ... })"
        )
         
    # 2. Check for .edited class
    if ".edited" not in rules:
         raise check50.Failure(
            "Missing CSS rules for class '.edited'",
            help="Style the edited span: .edited { color: green; font-weight: bold; }"
        )
