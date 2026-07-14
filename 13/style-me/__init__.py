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
    match = re.search(r'<div[^>]+class=["\']?([a-zA-Z0-9\-_]+)["\']?[^>]*>', html)
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
    
    # Locate selector rule for the card class
    pattern = r'\.' + re.escape(card_class) + r'\b\s*\{([^}]+)\}'
    match = re.search(pattern, css, re.DOTALL)
    
    if not match:
        raise check50.Failure(
            f"Could not find CSS rules for class '.{card_class}'",
            help=f"Define .{card_class} {{ ... }} either inside <style> tags in index.html, or in style.css"
        )
        
    rule_body = match.group(1)
    
    # 1. Border
    if "border" not in rule_body:
        raise check50.Failure(
            f"Class '.{card_class}' is missing a border property",
            help="Add 'border: 1px solid lightgray;' (or similar) to your card styles"
        )
    if not any(x in rule_body for x in ["gray", "grey", "d3d3d3", "light", "ccc", "eee"]):
        # Warn but pass if they customized the color, but let's check for standard light gray
        pass
        
    # 2. Border-radius
    if "border-radius" not in rule_body:
        raise check50.Failure(
            f"Class '.{card_class}' is missing a border-radius property",
            help="Add 'border-radius: 10px;' to round the card corners"
        )
        
    # 3. Padding
    if "padding" not in rule_body:
        raise check50.Failure(
            f"Class '.{card_class}' is missing a padding property",
            help="Add 'padding: 20px;' to create space between the content and the border"
        )
        
    # 4. Max-width
    if "max-width" not in rule_body:
        raise check50.Failure(
            f"Class '.{card_class}' is missing a max-width property",
            help="Add 'max-width: 400px;' to limit the card's width"
        )
