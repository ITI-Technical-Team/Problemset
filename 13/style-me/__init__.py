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
    # Check index.html style tags
    html = _read("index.html")
    style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE)
    for block in style_blocks:
        css_content += "\n" + block
    
    # Check style.css if it exists
    if os.path.exists("style.css"):
        css_content += "\n" + _read("style.css")
        
    return css_content.lower()


# ─── existence & structure ────────────────────────────────────────────────────

@check50.check()
def exists():
    """index.html exists"""
    check50.exists("index.html")


@check50.check(exists)
def has_card_div():
    """index.html contains a <div> with a class"""
    html = _html()
    match = re.search(r'<div[^+]+class=["\']?([a-zA-Z0-9\-_]+)["\']?[^>]*>', html)
    # Fallback search for class attribute in a div
    if not match:
        match = re.search(r'<div[^>]*class=["\']?([a-zA-Z0-9\-_]+)["\']?[^>]*>', html)
    if not match:
        raise check50.Failure(
            "Missing <div class=\"...\"> container in index.html",
            help="Add a <div> element with a class, e.g., class=\"card\""
        )
    return match.group(1)


@check50.check(has_card_div)
def has_h2_and_p(card_class):
    """the card contains an <h2> title and a <p> paragraph"""
    html = _html()
    # Check for h2
    if "<h2" not in html or "</h2>" not in html:
        raise check50.Failure("Missing <h2> heading for the title inside index.html")
    # Check for p
    if "<p" not in html or "</p>" not in html:
        raise check50.Failure("Missing <p> paragraph element inside index.html")


# ─── CSS style checks ─────────────────────────────────────────────────────────

@check50.check(has_card_div)
def checks_css_properties(card_class):
    """CSS sets border, border-radius, padding, and max-width on the card"""
    css = _get_css()
    
    # Strip comments first
    css_clean = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    
    # Locate selector rule for the card class
    pattern = r'\.' + re.escape(card_class) + r'\b\s*\{([^}]+)\}'
    match = re.search(pattern, css_clean, re.DOTALL)
    
    if not match:
        raise check50.Failure(
            f"Could not find CSS rules for class '.{card_class}'",
            help=f"Define .{card_class} {{ ... }} either inside <style> tags in index.html, or in style.css"
        )
        
    rule_body = match.group(1).strip()
    
    # Parse individual properties
    properties = {}
    for decl in rule_body.split(";"):
        if ":" in decl:
            prop, val = decl.split(":", 1)
            properties[prop.strip().lower()] = val.strip().lower()
            
    # 1. Border (specifically check for border property, not border-radius)
    has_border = False
    for p in properties:
        if p == "border" or (p.startswith("border-") and p != "border-radius"):
            has_border = True
            break
            
    if not has_border:
        raise check50.Failure(
            f"Class '.{card_class}' is missing a border property",
            help="Add 'border: 1px solid lightgray;' (or similar) to your card styles"
        )
        
    # Check color hints if possible
    border_val_str = " ".join([properties[p] for p in properties if p == "border" or (p.startswith("border-") and p != "border-radius")])
    if not any(x in border_val_str for x in ["gray", "grey", "d3d3d3", "light", "ccc", "eee"]):
        # Pass anyway since they might have customized the color
        pass
        
    # 2. Border-radius
    if "border-radius" not in properties:
        raise check50.Failure(
            f"Class '.{card_class}' is missing a border-radius property",
            help="Add 'border-radius: 10px;' to round the card corners"
        )
        
    # 3. Padding
    has_padding = "padding" in properties or any(p.startswith("padding-") for p in properties)
    if not has_padding:
        raise check50.Failure(
            f"Class '.{card_class}' is missing a padding property",
            help="Add 'padding: 20px;' to create space between the content and the border"
        )
        
    # 4. Max-width (or width)
    has_width = "max-width" in properties or "width" in properties
    if not has_width:
        raise check50.Failure(
            f"Class '.{card_class}' is missing a width or max-width property",
            help="Add 'max-width: 400px;' to limit the card's width"
        )
