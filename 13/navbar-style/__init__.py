import check50
import re
import os
from bs4 import BeautifulSoup


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _html():
    html = _read("index.html")
    clean_html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    return clean_html


def _get_css():
    """Retrieve all CSS content from index.html style tags and style.css (if it exists)"""
    css_content = ""
    html = _html()
    style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE)
    for block in style_blocks:
        css_content += "\n" + block
    
    if os.path.exists("style.css"):
        # Verify that index.html contains a link tag to style.css
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("link", rel=lambda r: r and r.lower() == "stylesheet")
        has_correct_link = False
        for link in links:
            href = link.get("href", "").strip().lower()
            if href in ["style.css", "./style.css"]:
                has_correct_link = True
                break
        if not has_correct_link:
            raise check50.Failure(
                "style.css is not correctly linked in index.html",
                help="Make sure to include `<link rel=\"stylesheet\" href=\"style.css\">` inside the <head> of index.html"
            )
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
    html = _html()
    soup = BeautifulSoup(html, "html.parser")
    if not soup.find("form"):
        raise check50.Failure(
            "Missing <form> element",
            help="Wrap your form elements inside a `<form>` tag"
        )


@check50.check(has_form)
def has_labels_and_inputs():
    """form contains label, input, and textarea elements for Name, Email, and Message"""
    html = _html()
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
    """form has a submit button with type="submit" """
    html = _html()
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        raise check50.Failure("Missing <form> element")
        
    has_btn = form.find("button", type=lambda t: t and t.lower() == "submit") or \
              form.find("input", type=lambda t: t and t.lower() == "submit")
              
    if not has_btn:
        if form.find("button") or form.find("input"):
            raise check50.Failure(
                "Submit button is missing type=\"submit\" attribute",
                help="Add type=\"submit\" to your button: `<button type=\"submit\">Send</button>`"
            )
        raise check50.Failure(
            "Missing submit button",
            help="Add a `<button type=\"submit\">Send</button>` or `<input type=\"submit\">` inside the form"
        )


@check50.check(has_form)
def checks_inputs_css():
    """CSS sets width, padding, and margin on inputs/textarea"""
    css_text = _get_css()
    rules = _parse_css(css_text)
    
    input_props = {}
    textarea_props = {}
    
    for sel, props in rules.items():
        if "input" in sel:
            input_props.update(props)
        if "textarea" in sel:
            textarea_props.update(props)
            
    # Check input fields
    if "width" not in input_props:
        raise check50.Failure(
            "Missing 'width' property on input fields inside CSS",
            help="Set 'width: 100%;' (or similar size) on your form input fields to make them fill the form container"
        )
    if "padding" not in input_props:
        raise check50.Failure(
            "Missing 'padding' property on input fields inside CSS",
            help="Set padding inside input fields to make them look clean"
        )
    if "margin" not in input_props and "margin-bottom" not in input_props:
        raise check50.Failure(
            "Missing 'margin' spacing property on input fields inside CSS",
            help="Add spacing (e.g. margin-bottom: 15px;) to separate your form input fields"
        )

    # Check textarea field
    if "width" not in textarea_props:
        raise check50.Failure(
            "Missing 'width' property on textarea inside CSS",
            help="Set 'width: 100%;' (or similar size) on your textarea field to make it fill the form container"
        )
    if "padding" not in textarea_props:
        raise check50.Failure(
            "Missing 'padding' property on textarea inside CSS",
            help="Set padding inside textarea field to make it look clean"
        )
    if "margin" not in textarea_props and "margin-bottom" not in textarea_props:
        raise check50.Failure(
            "Missing 'margin' spacing property on textarea inside CSS",
            help="Add spacing (e.g. margin-bottom: 15px;) to separate your form textarea field"
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
    normal_bg = button_props.get("background-color", button_props.get("background", ""))
    if not normal_bg:
        raise check50.Failure(
            "Submit button is missing a custom background-color",
            help="Style your button using 'background-color: ...;'"
        )
        
    # 2. Text color (must be white/light)
    color_val = button_props.get("color", "")
    if not color_val:
         raise check50.Failure(
            "Submit button is missing a text color property",
            help="Set the text color of the button to white (e.g., 'color: white;')"
        )
    if not any(x in color_val for x in ["white", "#fff", "#ffffff", "255,255,255"]):
         raise check50.Failure(
            "Submit button text color must be white",
            help="Set the text color of the button to white using `color: white;` or `color: #ffffff;`"
        )
         
    # 3. Padding
    if "padding" not in button_props:
        raise check50.Failure(
            "Submit button is missing a padding property",
            help="Add padding inside the button to make it larger and easier to click"
        )
        
    # 4. Hover state (must have background color and it must change)
    hover_bg = hover_props.get("background-color", hover_props.get("background", ""))
    if not hover_bg or not any(k in hover_props for k in ["background", "background-color"]):
        raise check50.Failure(
            "Missing hover style rule or background-color for the button in CSS (e.g., button:hover)",
            help="Add a hover effect (e.g., button:hover { background-color: #01293b; })"
        )
        
    if normal_bg == hover_bg:
        raise check50.Failure(
            "Submit button hover background color must be different from normal state",
            help="Change the background-color on button hover to a different color (e.g. darker background)"
        )
