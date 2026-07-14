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
def has_info_element():
    """index.html has an element with id='info'"""
    html = _html()
    if 'id="info"' not in html and "id='info'" not in html:
        raise check50.Failure(
            "Missing element with id='info'",
            help="Add a paragraph or div with id=\"info\" to hold the welcome message"
        )


@check50.check(exists)
def has_button_trigger():
    """index.html contains a button that calls showInfo()"""
    html = _html()
    if "<button" not in html:
        raise check50.Failure("Missing <button> element")
        
    # Check if button has onclick="showInfo()" or similar
    if "showinfo()" not in html:
        raise check50.Failure(
            "Button does not trigger showInfo() on click",
            help="Add onclick=\"showInfo()\" to your button"
        )


# ─── JS checks ────────────────────────────────────────────────────────────────

@check50.check(exists)
def has_showinfo_function():
    """JavaScript defines the showInfo() function"""
    html = _read("index.html")
    # Match function showInfo() or const showInfo = ...
    if "function showInfo" not in html and "const showInfo" not in html and "let showInfo" not in html:
        raise check50.Failure(
            "Missing showInfo() function",
            help="Define your click handler: function showInfo() { ... }"
        )


@check50.check(exists)
def js_prompts_and_updates():
    """showInfo() prompts for name, updates welcome message, and alerts user"""
    html = _html()
    if "prompt(" not in html:
        raise check50.Failure(
            "Missing prompt() call",
            help="Ask the user for their name: prompt('What is your name?')"
        )
    if "hello" not in html:
        raise check50.Failure(
            "Welcome message doesn't appear to greet the user with 'Hello'",
            help="Construct the message: 'Hello, ' + name + '!'"
        )
    if "alert(" not in html:
        raise check50.Failure(
            "Missing alert() confirmation",
            help="Call alert() inside showInfo() to confirm the update"
        )


# ─── CSS checks ───────────────────────────────────────────────────────────────

@check50.check(exists)
def checks_css_styling():
    """CSS styles the info text and the button"""
    html = _html()
    
    # Check for center alignment
    if "text-align" not in html or "center" not in html:
         raise check50.Failure(
            "Page content is not centered",
            help="Add 'text-align: center;' inside your CSS"
        )
         
    # Check selector for info
    if "#info" not in html:
        raise check50.Failure(
            "Missing CSS rules for #info",
            help="Style the welcome message: #info { font-size: 22px; color: darkblue; }"
        )
        
    # Check selector for button
    if "button" not in html:
        raise check50.Failure(
            "Missing CSS rules for button",
            help="Style your button with background color, padding, and border radius"
        )
        
    # Check button properties in CSS
    if "padding" not in html:
        raise check50.Failure("Button is missing a padding property in CSS")
    if "background-color" not in html:
        raise check50.Failure("Button is missing a background-color property in CSS")
    if "border-radius" not in html:
        raise check50.Failure("Button is missing a border-radius property in CSS")
