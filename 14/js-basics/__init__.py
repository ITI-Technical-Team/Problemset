import check50
import re


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _html():
    return _read("index.html").lower()


# ─── existence & structure ────────────────────────────────────────────────────

@check50.check()
def exists():
    """index.html exists"""
    check50.exists("index.html")


@check50.check(exists)
def has_script():
    """index.html contains a <script> block"""
    if "<script" not in _html():
        raise check50.Failure(
            "Missing <script> tag",
            help="Add a `<script>` element containing your JavaScript code inside index.html"
        )


@check50.check(exists)
def has_result_element():
    """index.html has a result element with id='result'"""
    html = _html()
    if 'id="result"' not in html and "id='result'" not in html:
        raise check50.Failure(
            "Missing element with id='result'",
            help="Add an HTML element like `<p id=\"result\"></p>` to display the age category"
        )


# ─── JS checks ────────────────────────────────────────────────────────────────

@check50.check(has_script)
def has_arrow_function():
    """JavaScript defines checkAge as an arrow function"""
    html = _read("index.html")
    # Search for checkAge = (...) => or checkAge = age =>
    # Also handle whitespaces
    pattern = r'const\s+checkAge\s*=\s*(?:\([^)]*\)|[a-zA-Z0-9\-_]+)\s*=>'
    if not re.search(pattern, html):
        raise check50.Failure(
            "Missing checkAge arrow function definition",
            help="Define your function as an arrow function: const checkAge = (age) => { ... }"
        )


@check50.check(has_script)
def prompts_user():
    """JavaScript prompts the user for their age"""
    if "prompt(" not in _html():
        raise check50.Failure(
            "Missing prompt() call",
            help="Ask the user to enter their age using a prompt, e.g. prompt('Enter your age:')"
        )


@check50.check(has_script)
def uses_alert_and_innertext():
    """JavaScript uses alert() and updates result element's text and class"""
    html = _html()
    if "alert(" not in html:
        raise check50.Failure(
            "Missing alert() call inside checkAge",
            help="Use alert() to popup the age category to the user"
        )
    if "innertext" not in html and "innerhtml" not in html and "textcontent" not in html:
        raise check50.Failure(
            "Does not update the result element's text content",
            help="Use resultElement.innerText = ... to show the category on the web page"
        )
    if "classname" not in html and "classlist" not in html:
        raise check50.Failure(
            "Does not update the result element's CSS class",
            help="Use resultElement.className = ... to style the result differently depending on the category"
        )


# ─── CSS checks ───────────────────────────────────────────────────────────────

@check50.check(exists)
def has_css_classes():
    """CSS defines classes for child, teenager, and adult categories"""
    html = _html()
    for category in ["child", "teenager", "adult"]:
        # Match .child, .teenager, .adult inside <style>
        pattern = r'\.' + category + r'\b'
        if not re.search(pattern, html):
            raise check50.Failure(
                f"Missing CSS rule for class '.{category}'",
                help=f"Define .{category} {{ color: ...; }} in your style block"
            )
            
    if "text-align" not in html or "center" not in html:
        raise check50.Failure(
            "Content is not centered via CSS",
            help="Add 'text-align: center;' to center all elements on the page"
        )
