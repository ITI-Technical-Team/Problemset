import check50
import re
from bs4 import BeautifulSoup


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


@check50.check()
def exists():
    """index.html exists"""
    check50.exists("index.html")


@check50.check(exists)
def has_doctype():
    """index.html has <!DOCTYPE html>"""
    raw = _read("index.html")
    uncommented = re.sub(r'<!--.*?-->', '', raw, flags=re.DOTALL)
    if not re.search(r'<!doctype\s+html', uncommented, re.IGNORECASE):
        raise check50.Failure(
            "Missing <!DOCTYPE html> declaration in index.html",
            help="The first line of your HTML file must be <!DOCTYPE html>"
        )


@check50.check(has_doctype)
def test_html_structure():
    """index.html contains all required non-empty elements (container div, h1, 2 paragraphs, valid img, ul of 4, link with target="_blank")"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    
    # Check container
    container = soup.find(class_="container") or soup.find(id="container")
    if not container:
        raise check50.Failure(
            "Missing a container <div> element with class=\"container\"",
            help="Add a `<div class=\"container\">` wrapping your hobby content"
        )
        
    h1 = container.find("h1")
    if not h1 or not h1.get_text().strip():
        raise check50.Failure("Missing or empty main heading <h1> inside container")
        
    paragraphs = [p for p in container.find_all("p") if p.get_text().strip()]
    if len(paragraphs) < 2:
        raise check50.Failure(
            f"Found {len(paragraphs)} non-empty paragraph(s) inside container, expected at least 2",
            help="Add at least 2 paragraphs with descriptive text about your favorite hobby inside the container"
        )
        
    img = container.find("img")
    src = img.get("src", "").strip() if img else ""
    if not img or not src:
        raise check50.Failure("Missing <img> or missing src attribute inside container")
        
    valid_exts = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".avif")
    src_clean = src.split("?")[0].split("#")[0].lower()
    is_img = (
        src.startswith("data:image/") or
        any(src_clean.endswith(ext) for ext in valid_exts) or
        any(ext in src_clean for ext in valid_exts)
    )
    if not is_img or src.endswith("/") or re.search(r'\.(html?|php|asp|jsp)\b', src, re.I):
        raise check50.Failure(
            f"The <img> 'src' attribute '{src}' does not point to a valid image file",
            help="Make sure src points to an image file (e.g. hobby.jpg, photo.png, or a valid image URL)."
        )
        
    ul = container.find("ul")
    if not ul:
        raise check50.Failure("Missing unordered list <ul> inside container")
    items = [li for li in ul.find_all("li") if li.get_text().strip()]
    if len(items) < 4:
        raise check50.Failure(
            f"Found {len(items)} non-empty item(s) in unordered list, expected at least 4",
            help="Add at least 4 hobbies or activities with text inside <li> items in your <ul> list"
        )
        
    link = container.find("a")
    if not link or not link.get("href", "").strip():
        raise check50.Failure("Missing hyperlink <a> or missing href attribute inside container")
    if not link.get_text().strip():
        raise check50.Failure(
            "Found an empty <a> tag inside container",
            help="Your <a> link tag must contain visible link text, e.g. <a href=\"...\" target=\"_blank\">Learn More</a>"
        )
        
    target = link.get("target", "").strip()
    if target != "_blank":
        raise check50.Failure(
            "Hyperlink does not open in a new tab",
            help="Add target=\"_blank\" to your <a> tag"
        )


@check50.check(has_doctype)
def test_css_styling():
    """index.html uses Internal CSS with required active rules and hover selectors"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    style = soup.find("style")
    if not style:
        raise check50.Failure(
            "Missing <style> block inside <head>",
            help="Use Internal CSS by adding a `<style>` element inside the `<head>` section"
        )
        
    # Strip CSS comments /* ... */ to prevent commented-out styles from passing
    css = re.sub(r'/\*.*?\*/', '', style.get_text(), flags=re.DOTALL).lower()
    
    # Check body styles
    if "background" not in css or "color" not in css:
        raise check50.Failure("Missing background-color or text color style rules in active CSS")
    if "font-family" not in css:
        raise check50.Failure("Missing font-family declaration in active CSS")
    if "font-size" not in css:
        raise check50.Failure("Missing font-size declaration in active CSS")
    if "line-height" not in css:
        raise check50.Failure("Missing line-height declaration in active CSS")
        
    # Check heading styles
    if "h1" not in css:
        raise check50.Failure("Missing CSS rule for h1 selector")
    if "text-align" not in css or "center" not in css:
        raise check50.Failure("Main heading h1 is not centered using text-align: center")
    if "font-weight" not in css or "bold" not in css:
        raise check50.Failure("Main heading h1 is not styled as bold using font-weight")
        
    # Check paragraph styles
    if "p" not in css:
        raise check50.Failure("Missing CSS rule for p selector")
    if "font-style" not in css or "italic" not in css:
        raise check50.Failure("Paragraphs are not styled as italic using font-style: italic")
    if "letter-spacing" not in css:
        raise check50.Failure("Paragraphs do not have letter-spacing set")
        
    # Check container class selector styling
    if ".container" not in css:
        raise check50.Failure("Missing CSS selector for '.container' class")
    for prop in ["width", "max-width", "margin", "padding", "background", "border"]:
        if prop not in css:
            raise check50.Failure(
                f"Missing box model/layout property '{prop}' in active CSS styles"
            )
            
    # Check hover selector
    if "hover" not in css:
        raise check50.Failure(
            "Missing hover state styling (e.g. a:hover)",
            help="Style links on hover using a:hover selector"
        )
    if "underline" not in css or "text-decoration" not in css:
        raise check50.Failure(
            "Hover link styling is missing text-decoration: underline"
        )
