import check50
import re
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
    """index.html contains a button, text input, and script tag"""
    _check_tag_closed("index.html", "html")
    _check_tag_closed("index.html", "body")
    _check_tag_closed("index.html", "script")

    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")

    # Check for button
    btn = soup.find("button")
    if not btn:
        raise check50.Failure(
            "Missing button tag",
            help="Add a <button> tag to index.html"
        )

    # Check for input type text
    inp = soup.find("input")
    if not inp:
        raise check50.Failure(
            "Missing input tag",
            help="Add an <input> tag to index.html"
        )

    # Verify input has type text or no type (default is text)
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

    # Look for common inline event attributes: onclick, onmouseover, onmouseout, onkeydown, onkeyup, onchange
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
    """JavaScript uses addEventListener for the text input"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    js_raw = soup.find("script").string or ""

    if "addEventListener" not in js_raw:
        raise check50.Failure(
            "addEventListener not found in script",
            help="Use addEventListener to listen to events on the text input (e.g. input.addEventListener('keyup', ...))"
        )
