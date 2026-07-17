import check50
import re
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
    # Standardize whitespace and remove commas/attributes spacing
    sel = re.sub(r'\s+', ' ', sel.strip().lower())
    # Remove spacing around characters like >, +, ~, :
    sel = re.sub(r'\s*([>+~:])\s*', r'\1', sel)
    return sel


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
def has_form():
    """index.html has a <form> element"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    if not soup.find("form"):
        raise check50.Failure(
            "Missing <form> element",
            help="Wrap your form elements inside a `<form>` tag"
        )


@check50.check(has_form)
def has_labels_and_inputs():
    """form contains label, input, and textarea elements for Name, Email, and Message"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        raise check50.Failure("Missing <form> element")
        
    # Check for Name input (text input)
    inputs = form.find_all("input")
    has_text = any(inp.get("type", "text").lower() == "text" for inp in inputs)
    if not has_text and not form.find("input"):
        raise check50.Failure("Missing <input> elements inside the form")
        
    # Check for Email input
    has_email = any(inp.get("type", "").lower() == "email" for inp in inputs)
    if not has_email:
        raise check50.Failure(
            "Missing <input type=\"email\">",
            help="Make sure to use type=\"email\" for the Email input field"
        )
        
    # Check for Message textarea
    if not form.find("textarea"):
        raise check50.Failure(
            "Missing <textarea> for the Message field",
            help="Use a `<textarea>` tag for multi-line user messages"
        )
        
    # Check for labels
    labels = form.find_all("label")
    if len(labels) < 3:
        raise check50.Failure(
            f"Found {len(labels)} <label> element(s) inside the form, expected at least 3",
            help="Add `<label>` tags for Name, Email, and Message"
        )


@check50.check(has_form)
def has_submit_button():
    """form has a submit button"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        raise check50.Failure("Missing <form> element")
        
    has_btn = form.find("button") or \
              form.find("input", type=lambda t: t and t.lower() == "submit")
              
    if not has_btn:
        raise check50.Failure(
            "Missing submit button",
            help="Add a `<button type=\"submit\">Send</button>` or `<input type=\"submit\">` inside the form"
        )


# ─── CSS style checks ─────────────────────────────────────────────────────────

@check50.check(has_form)
def checks_inputs_css():
    """CSS sets width, padding, and margin on inputs/textarea"""
    css_text = _get_css()
    rules = _parse_css(css_text)
    
    # We look for styles targeting input, textarea
    # Properties should be defined on selectors like 'input', 'textarea', or combined input/textarea rules
    target_selectors = ["input", "textarea", "input,textarea", "textarea,input"]
    
    # Find all properties defined for any selector containing input or textarea
    input_props = {}
    for sel, props in rules.items():
        if "input" in sel or "textarea" in sel:
            input_props.update(props)
            
    if "width" not in input_props:
        raise check50.Failure(
            "Missing 'width' property on inputs/textarea inside CSS",
            help="Set 'width: 100%;' (or similar size) on your form fields to make them fill the form container"
        )
    if "padding" not in input_props:
        raise check50.Failure(
            "Missing 'padding' property on inputs/textarea inside CSS",
            help="Set padding inside input and textarea fields to make them look clean"
        )
    if "margin" not in input_props and "margin-bottom" not in input_props:
        raise check50.Failure(
            "Missing 'margin' spacing property on inputs/textarea inside CSS",
            help="Add spacing (e.g. margin-bottom: 15px;) to separate your form fields"
        )


@check50.check(has_form)
def checks_button_css():
    """CSS styles the submit button with background, color, padding, and hover state"""
    css_text = _get_css()
    rules = _parse_css(css_text)
    
    # Locate properties defined for any selector containing button or input[type=submit]
    button_props = {}
    hover_props = {}
    
    for sel, props in rules.items():
        if "button" in sel or "submit" in sel:
            if "hover" in sel:
                hover_props.update(props)
            else:
                button_props.update(props)
                
    # 1. Background color
    if not any(k in button_props for k in ["background", "background-color"]):
        raise check50.Failure(
            "Submit button is missing a custom background-color",
            help="Style your button using 'background-color: ...;'"
        )
        
    # 2. Text color
    if "color" not in button_props:
         raise check50.Failure(
            "Submit button is missing a text color property",
            help="Set the text color of the button (e.g., 'color: white;')"
        )
         
    # 3. Padding
    if "padding" not in button_props:
        raise check50.Failure(
            "Submit button is missing a padding property",
            help="Add padding inside the button to make it larger and easier to click"
        )
        
    # 4. Hover state
    # We expect a selector like 'button:hover' or 'input[type=submit]:hover' to exist
    has_hover = False
    for sel in rules:
        if ("button:hover" in sel or "submit:hover" in sel or "button" in sel) and "hover" in sel:
            has_hover = True
            break
            
    if not has_hover:
        raise check50.Failure(
            "Missing hover style rule for the button in CSS (e.g., button:hover)",
            help="Add a hover effect (e.g., button:hover { background-color: ...; })"
        )
