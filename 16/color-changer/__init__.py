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
def has_quote_elements():
    """index.html has elements with id='quote' and id='author'"""
    html = _html()
    if 'id="quote"' not in html and "id='quote'" not in html:
        raise check50.Failure(
            "Missing element with id='quote'",
            help="Add an HTML element like `<p id=\"quote\"></p>` to display the quote text"
        )
    if 'id="author"' not in html and "id='author'" not in html:
         raise check50.Failure(
            "Missing element with id='author'",
            help="Add an HTML element like `<p id=\"author\"></p>` to display the author's name"
        )


@check50.check(exists)
def has_button():
    """index.html contains a button to generate new quote"""
    html = _html()
    if "<button" not in html:
         raise check50.Failure("Missing <button> element")
    if "randomquotes()" not in html:
         raise check50.Failure(
            "Button does not call RandomQuotes()",
            help="Add onclick=\"RandomQuotes()\" to your button"
        )


# ─── JS checks ────────────────────────────────────────────────────────────────

@check50.check(exists)
def has_quotes_data():
    """JavaScript declares the quotes object with at least 10 items"""
    html = _read("index.html").lower()
    if "quotes" not in html:
        raise check50.Failure(
            "Missing 'quotes' variable",
            help="Declare a quotes object containing 10 different quotes"
        )
    # Check for Oscar Wilde in the code
    if "oscar wilde" not in html:
        raise check50.Failure(
            "Quotes object is missing required quotes",
            help="Make sure to include the 10 quotes provided in the pset description"
        )


@check50.check(exists)
def defines_randomquotes_function():
    """JavaScript defines the RandomQuotes() function"""
    html = _read("index.html")
    if "function RandomQuotes" not in html and "const RandomQuotes" not in html and "let RandomQuotes" not in html:
         raise check50.Failure(
            "Missing RandomQuotes() function",
            help="Define the function: function RandomQuotes() { ... }"
        )


@check50.check(exists)
def uses_random_math():
    """RandomQuotes() uses Math.random() and Math.floor() to select a quote"""
    html = _html()
    if "math.random" not in html:
        raise check50.Failure("Missing Math.random() call")
    if "math.floor" not in html:
        raise check50.Failure("Missing Math.floor() call")
    if "10" not in html:
         raise check50.Failure(
            "Does not multiply Math.random() by 10",
            help="Generate an index between 0 and 9: Math.floor(Math.random() * 10)"
        )


@check50.check(exists)
def updates_quote_text():
    """RandomQuotes() updates innerHTML or innerText of quote and author elements"""
    html = _html()
    if "innerhtml" not in html and "innertext" not in html and "textcontent" not in html:
         raise check50.Failure(
            "Does not update the quote and author elements text on the page",
            help="Use quoteElement.innerHTML or innerText to output the selected quote"
        )
