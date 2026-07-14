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
def has_html_structure():
    """index.html contains heading #title and 3 paragraphs with class 'info'"""
    html = _html()
    
    # Check title element
    if 'id="title"' not in html and "id='title'" not in html:
        raise check50.Failure(
            "Missing heading with id='title'",
            help="Add a heading: <h1 id=\"title\">Welcome to JavaScript!</h1>"
        )
        
    # Check paragraphs
    paragraphs = re.findall(r'<p[^>]+class=["\']?info["\']?[^>]*>', html)
    if len(paragraphs) != 3:
        raise check50.Failure(
            f"Found {len(paragraphs)} paragraph(s) with class 'info', expected exactly 3",
            help="Add exactly three `<p class=\"info\">` elements"
        )
        
    # Check button
    if "<button" not in html:
         raise check50.Failure("Missing <button> element")
    if "editparagraphs()" not in html:
         raise check50.Failure(
            "Button does not trigger editParagraphs() on click",
            help="Add onclick=\"editParagraphs()\" to your button"
        )


# ─── JS checks ────────────────────────────────────────────────────────────────

@check50.check(exists)
def has_edit_paragraphs_function():
    """JavaScript defines editParagraphs() function"""
    html = _read("index.html")
    if "function editParagraphs" not in html and "const editParagraphs" not in html and "let editParagraphs" not in html:
        raise check50.Failure(
            "Missing editParagraphs() function",
            help="Define the function: function editParagraphs() { ... }"
        )


@check50.check(exists)
def js_dom_selection_and_loop():
    """editParagraphs() uses querySelectorAll() and forEach()"""
    html = _html()
    if "queryselectorall" not in html:
        raise check50.Failure(
            "Missing querySelectorAll() call",
            help="Use document.querySelectorAll('.info') to select the paragraphs"
        )
    if "foreach" not in html:
        raise check50.Failure(
            "Missing .forEach() loop",
            help="Use .forEach() to iterate over the selected paragraphs"
        )


@check50.check(exists)
def js_paragraph_modification():
    """editParagraphs() converts text to uppercase, replaces 'paragraph' with 'sentence', and wraps in span class 'edited'"""
    html = _html()
    if "touppercase()" not in html:
        raise check50.Failure(
            "Missing .toUpperCase() call",
            help="Convert the paragraph text to uppercase inside the loop"
        )
    if "replace(" not in html:
        raise check50.Failure(
            "Missing .replace() call",
            help="Use .replace('PARAGRAPH', 'SENTENCE') to replace the word"
        )
    if "innerhtml" not in html:
        raise check50.Failure(
            "Missing innerHTML update on paragraphs",
            help="Update the paragraph's innerHTML inside the loop"
        )
    if "edited" not in html:
        raise check50.Failure(
            "Does not wrap updated text in a span with class 'edited'",
            help="Wrap the text: `<span class=\"edited\">${updated}</span>`"
        )


@check50.check(exists)
def js_title_modification():
    """editParagraphs() appends ' - Edited' to the title"""
    html = _html()
    if "edited" not in html or "title" not in html:
        raise check50.Failure("Does not appear to update the title's content")
        
    # Check for appending logic
    if "+=" not in html and "concat" not in html and "title.innerhtml = title.innerhtml" not in html:
         raise check50.Failure(
            "Does not append ' - Edited' to the heading content",
            help="Use title.innerHTML += ' - Edited' or similar to append to the heading"
        )


# ─── CSS checks ───────────────────────────────────────────────────────────────

@check50.check(exists)
def checks_css_styling():
    """CSS styles the page and defines class '.edited'"""
    html = _html()
    if "text-align" not in html or "center" not in html:
         raise check50.Failure(
            "Page content is not centered",
            help="Add 'text-align: center;' inside your CSS"
        )
    if ".edited" not in html:
         raise check50.Failure(
            "Missing CSS rules for class '.edited'",
            help="Style the edited span: .edited { color: green; font-weight: bold; }"
        )
