import check50
import re
from bs4 import BeautifulSoup


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


@check50.check()
def exists():
    """index.html and style.css exist"""
    check50.exists("index.html")
    check50.exists("style.css")


@check50.check(exists)
def test_stylesheet_link():
    """index.html links to style.css"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    link = soup.find("link", rel="stylesheet")
    if not link:
        raise check50.Failure(
            "index.html is missing a <link> to a stylesheet",
            help="Add `<link rel=\"stylesheet\" href=\"style.css\">` inside the `<head>` section"
        )
    href = link.get("href", "").strip()
    if href != "style.css":
        raise check50.Failure(
            f"Expected stylesheet link href to be 'style.css', but got '{href}'",
            help="Link your external stylesheet exactly as `style.css`"
        )


@check50.check(exists)
def test_html_structure():
    """index.html contains required non-empty elements (container div, header, skills section, projects section, contact link)"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    
    # Check container
    container = soup.find(class_="container")
    if not container:
        raise check50.Failure(
            "Missing a container <div> element with class=\"container\"",
            help="Add a `<div class=\"container\">` wrapping your portfolio content"
        )
        
    header = container.find("header") or container.find(id="header")
    if not header:
        raise check50.Failure("Missing <header> element inside container")
        
    # Check skills list
    ul = container.find("ul")
    if not ul:
        raise check50.Failure("Missing unordered list <ul> inside container")
    items = [li for li in ul.find_all("li") if li.get_text().strip()]
    if len(items) < 5:
        raise check50.Failure(
            f"Found {len(items)} non-empty item(s) in unordered list, expected at least 5 skills",
            help="Add at least 5 skills as <li> items with text inside your <ul> list"
        )
        
    # Check projects section
    paragraphs = [p for p in container.find_all("p") if p.get_text().strip()]
    if len(paragraphs) < 2:
        p_texts = [p.get_text().lower() for p in paragraphs]
        has_proj_p = any("project" in t or "web" in t or "work" in t for t in p_texts)
        if not has_proj_p:
            raise check50.Failure(
                "Missing non-empty paragraph <p> describing your projects inside container"
            )
            
    # Check contact link
    link = container.find("a")
    if not link or not link.get("href", "").strip():
        raise check50.Failure("Missing Contact Me hyperlink <a> or missing href attribute inside container")
    if not link.get_text().strip():
        raise check50.Failure(
            "Found an empty Contact Me hyperlink <a> inside container",
            help="Add visible text to your contact link <a> tag"
        )


@check50.check(exists)
def test_css_styling():
    """style.css contains all required CSS selectors and active properties"""
    raw_css = _read("style.css")
    # Strip CSS comments /* ... */ to prevent commented-out styles from passing
    css = re.sub(r'/\*.*?\*/', '', raw_css, flags=re.DOTALL).lower()
    
    # Check selector types
    has_element_sel = any(sel in css for sel in ["body", "h1", "h2", "p", "ul", "li", "header", "a"])
    if not has_element_sel:
        raise check50.Failure("style.css is missing element selectors (e.g., body, h1)")
        
    # 2. Class selector (e.g. .container)
    if ".container" not in css:
        raise check50.Failure(
            "style.css is missing class selector '.container'",
            help="Use a class selector (.container) to style your container div"
        )
        
    # 3. ID selector (e.g. #contact-link or similar)
    if "#" not in css:
        raise check50.Failure(
            "style.css is missing an ID selector (e.g., #contact-link)",
            help="Apply an ID selector (using `#`) to style an individual element on your page"
        )
        
    # Check colors (Hex, RGB, or Name)
    if "color" not in css and "background" not in css:
        raise check50.Failure("style.css is missing active color properties")
        
    # Check typography properties
    for prop in ["font-family", "font-size", "font-weight", "line-height", "letter-spacing", "text-align"]:
        if prop not in css:
            raise check50.Failure(f"style.css is missing active typography property '{prop}'")
            
    # Check container box model properties
    for prop in ["width", "max-width", "margin", "padding", "background", "border"]:
        if prop not in css:
            raise check50.Failure(
                f"style.css is missing active box model/layout property '{prop}' in CSS styles"
            )
            
    # Check hover selector
    if "hover" not in css:
        raise check50.Failure(
            "style.css is missing hover state selector (e.g. a:hover or #contact-link:hover)",
            help="Style your link hover state using `:hover` selector"
        )
    if "text-decoration" not in css:
        raise check50.Failure("style.css is missing active text-decoration styling in hover rule")
