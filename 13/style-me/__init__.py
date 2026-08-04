import check50
import re
import os
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


def _html():
    html = _read("index.html")
    clean_html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    return clean_html


def _get_css():
    """Retrieve all CSS content from index.html style tags and style.css (if it exists)"""
    css_content = ""
    # Check index.html style tags
    html = _read("index.html")
    clean_html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', clean_html, re.DOTALL | re.IGNORECASE)
    for block in style_blocks:
        css_content += "\n" + block
    
    # Check style.css if it exists
    if os.path.exists("style.css"):
        # Verify that index.html contains a link tag to style.css
        soup = BeautifulSoup(clean_html, "html.parser")
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


# ─── existence & structure ────────────────────────────────────────────────────

@check50.check()
def exists():
    """index.html exists"""
    check50.exists("index.html")


@check50.check(exists)
def has_card_div():
    """index.html contains a <div> with a class"""
    _check_tag_closed("index.html", "html")
    _check_tag_closed("index.html", "head")
    _check_tag_closed("index.html", "body")
    _check_tag_closed("index.html", "div")
    html = _html()
    match = re.search(r'<div[^+]+class=["\']?([a-zA-Z0-9\-_]+)["\']?[^>]*>', html, re.IGNORECASE)
    # Fallback search for class attribute in a div
    if not match:
        match = re.search(r'<div[^>]*class=["\']?([a-zA-Z0-9\-_]+)["\']?[^>]*>', html, re.IGNORECASE)
    if not match:
        raise check50.Failure(
            "Missing <div class=\"...\"> container in index.html",
            help="Add a <div> element with a class, e.g., class=\"card\""
        )
    return match.group(1)


@check50.check(has_card_div)
def has_h2_and_p(card_class):
    """the card contains an <h2> title and a <p> paragraph"""
    _check_tag_closed("index.html", "h2")
    _check_tag_closed("index.html", "p")
    html = _html().lower()
    # Check for h2
    if "<h2" not in html or "</h2>" not in html:
        raise check50.Failure("Missing <h2> heading for the title inside index.html")
    # Check for p
    if "<p" not in html or "</p>" not in html:
        raise check50.Failure("Missing <p> paragraph element inside index.html")


# ─── CSS style checks ─────────────────────────────────────────────────────────

@check50.check(has_card_div)
def checks_css_properties(card_class):
    """CSS sets border, border-radius, padding, max-width, and centering on the card"""
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
        
    # Get active border color
    def _is_grey(color_str):
        color_str = color_str.strip().lower()
        grey_names = {
            "gray", "grey", "lightgray", "lightgrey", "darkgray", "darkgrey",
            "dimgray", "dimgrey", "slategray", "slategrey", "gainsboro", "silver",
            "whitesmoke", "ghostwhite", "lightslategray", "lightslategrey"
        }
        if color_str in grey_names:
            return True
        hex_match = re.match(r'^#([0-9a-f]{3}|[0-9a-f]{6})$', color_str)
        if hex_match:
            val = hex_match.group(1)
            if len(val) == 3:
                return val[0] == val[1] == val[2]
            elif len(val) == 6:
                return val[0:2] == val[2:4] == val[4:6]
        rgb_match = re.match(r'^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*[\d\.]+\s*)?\)$', color_str)
        if rgb_match:
            r, g, b = rgb_match.groups()
            return r == g == b
        hsl_match = re.match(r'^hsla?\(\s*\d+\s*,\s*0%?\s*,\s*[\d%]+\s*(?:,\s*[\d\.]+\s*)?\)$', color_str)
        if hsl_match:
            return True
        return False

    def _extract_color(border_val):
        border_val = border_val.strip().lower()
        func_match = re.search(r'(?:rgba?|hsla?)\([^\)]+\)', border_val)
        if func_match:
            return func_match.group(0)
        hex_match = re.search(r'#[0-9a-f]{3,6}\b', border_val)
        if hex_match:
            return hex_match.group(0)
        words = re.findall(r'\b[a-zA-Z]+\b', border_val)
        styles_and_widths = {
            "solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset", "none", "hidden",
            "thin", "medium", "thick", "px", "em", "rem", "pt"
        }
        colors = [w for w in words if w not in styles_and_widths]
        if colors:
            return colors[0]
        return ""

    border_color = ""
    if "border-color" in properties:
        border_color = properties["border-color"]
    else:
        for side in ["top", "right", "bottom", "left"]:
            if f"border-{side}-color" in properties:
                border_color = properties[f"border-{side}-color"]
                break
        if not border_color:
            for prop_name in ["border", "border-top", "border-right", "border-bottom", "border-left"]:
                if prop_name in properties:
                    border_color = _extract_color(properties[prop_name])
                    if border_color:
                        break

    if not border_color:
        raise check50.Failure(
            f"Class '.{card_class}' has border property, but border color could not be determined",
            help="Define your border color clearly, e.g. border: 1px solid lightgray;"
        )
    if not _is_grey(border_color):
        raise check50.Failure(
            f"Border color '{border_color}' is not a shade of grey",
            help="Set your border color to a light grey color (e.g. lightgray or #ccc)"
        )
        
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

    # 5. Centering (margin containing auto)
    has_margin_auto = False
    for p, v in properties.items():
        if p == "margin" or p.startswith("margin-"):
            if "auto" in v:
                has_margin_auto = True
                break
    if not has_margin_auto:
        raise check50.Failure(
            f"Class '.{card_class}' is not centered using margin auto",
            help="Add 'margin: 50px auto;' or 'margin: auto;' to center the card on the page"
        )
