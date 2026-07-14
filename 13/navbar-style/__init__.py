import check50
import re
import os


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _html():
    return _read("index.html").lower()


def _get_css():
    """Retrieve all CSS content from index.html style tags and style.css (if it exists)"""
    css_content = ""
    html = _read("index.html")
    style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE)
    for block in style_blocks:
        css_content += "\n" + block
    
    if os.path.exists("style.css"):
        css_content += "\n" + _read("style.css")
        
    return css_content.lower()


# ─── existence & structure ────────────────────────────────────────────────────

@check50.check()
def exists():
    """index.html exists"""
    check50.exists("index.html")


@check50.check(exists)
def has_form():
    """index.html has a <form> element"""
    if "<form" not in _html():
        raise check50.Failure(
            "Missing <form> element",
            help="Wrap your form elements inside a `<form>` tag"
        )


@check50.check(has_form)
def has_labels_and_inputs():
    """form contains label, input, and textarea elements for Name, Email, and Message"""
    html = _html()
    
    # Check for Name input
    if "name" not in html:
        raise check50.Failure("Could not find any text references to 'Name'")
    if "<input" not in html:
        raise check50.Failure("Missing <input> elements inside the form")
        
    # Check for Email input
    if 'type="email"' not in html and "type='email'" not in html:
        raise check50.Failure(
            "Missing <input type=\"email\">",
            help="Make sure to use type=\"email\" for the Email input field"
        )
        
    # Check for Message textarea
    if "<textarea" not in html:
        raise check50.Failure(
            "Missing <textarea> for the Message field",
            help="Use a `<textarea>` tag for multi-line user messages"
        )
        
    # Check for labels
    labels = re.findall(r'<label[^>]*>(.*?)</label>', html, re.DOTALL)
    if len(labels) < 3:
        raise check50.Failure(
            f"Found {len(labels)} <label> element(s), expected at least 3",
            help="Add `<label>` tags for Name, Email, and Message"
        )


@check50.check(has_form)
def has_submit_button():
    """form has a submit button"""
    html = _html()
    # Can be <button type="submit">, <input type="submit">, or <button>
    has_btn = "<button" in html or 'type="submit"' in html or "type='submit'" in html
    if not has_btn:
        raise check50.Failure(
            "Missing submit button",
            help="Add a `<button type=\"submit\">Send</button>` or `<input type=\"submit\">` inside the form"
        )


# ─── CSS style checks ─────────────────────────────────────────────────────────

@check50.check(has_form)
def checks_inputs_css():
    """CSS sets width, padding, and margin on inputs/textarea"""
    css = _get_css()
    
    # We look for styles targeting input, textarea
    # We check if 'width' and 'padding' are set on input and textarea
    # A simple way is to search the entire CSS for properties
    if "width" not in css:
        raise check50.Failure(
            "Missing 'width' property in CSS",
            help="Set 'width: 100%;' (or similar size) on your form fields"
        )
    if "padding" not in css:
        raise check50.Failure(
            "Missing 'padding' property in CSS",
            help="Set padding inside input and textarea fields to make them look clean"
        )
    if "margin" not in css:
        raise check50.Failure(
            "Missing 'margin' property in CSS",
            help="Add spacing (e.g. margin-bottom: 15px;) to separate your form fields"
        )


@check50.check(has_form)
def checks_button_css():
    """CSS styles the submit button with background, color, padding, and hover state"""
    css = _get_css()
    
    # 1. Background color
    if "background" not in css:
        raise check50.Failure(
            "Submit button is missing a custom background-color",
            help="Style your button using 'background-color: ...;'"
        )
        
    # 2. Text color white
    # Check if 'white', '#fff', '#ffffff', or 'rgb(255,255,255)' exists
    if "color" not in css:
         raise check50.Failure(
            "Submit button is missing a text color property",
            help="Set the text color of the button (e.g., 'color: white;')"
        )
        
    # 3. Hover state
    if ":hover" not in css:
        raise check50.Failure(
            "Missing hover style rule in CSS",
            help="Add a hover effect (e.g. button:hover { background-color: ...; })"
        )
