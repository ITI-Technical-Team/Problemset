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
    """index.html contains required non-empty elements (div with id='profile', valid img, h1 with class='title', p, ol, link)"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    
    # Check profile div
    profile = soup.find(id="profile")
    if not profile:
        raise check50.Failure(
            "Missing a profile card <div> element with id=\"profile\"",
            help="Add a `<div id=\"profile\">` wrapping your student card content"
        )
        
    img = profile.find("img")
    src = img.get("src", "").strip() if img else ""
    if not img or not src:
        raise check50.Failure("Missing <img> or missing src attribute inside profile card")
        
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
            help="Make sure src points to an image file (e.g. photo.jpg, avatar.png, or a valid image URL)."
        )
        
    h1 = profile.find("h1")
    if not h1 or not h1.get_text().strip():
        raise check50.Failure("Missing or empty student name heading <h1> inside profile card")
        
    classes = h1.get("class", [])
    if "title" not in classes:
        raise check50.Failure(
            "Student name heading <h1> is missing the class name '.title'",
            help="Add class=\"title\" to your <h1> heading inside the profile card"
        )
        
    p = profile.find("p")
    if not p or not p.get_text().strip():
        raise check50.Failure("Missing or empty short description paragraph <p> inside profile card")
        
    ol = profile.find("ol")
    if not ol:
        raise check50.Failure("Missing ordered list <ol> inside profile card")
    items = [li for li in ol.find_all("li") if li.get_text().strip()]
    if len(items) < 2:
        raise check50.Failure(
            f"Found {len(items)} non-empty item(s) in ordered list, expected at least 2",
            help="Add your learning goals as text inside <li> items inside your <ol> list"
        )
        
    link = profile.find("a")
    if not link or not link.get("href", "").strip():
        raise check50.Failure("Missing portfolio link <a> or missing href attribute inside profile card")
    if not link.get_text().strip():
        raise check50.Failure(
            "Found an empty portfolio link <a> inside profile card",
            help="Add visible text to your portfolio link <a> tag"
        )


@check50.check(has_doctype)
def test_css_styling():
    """index.html uses Internal CSS with class and ID selectors, box model, and hover selectors"""
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
    
    # Check ID selector
    if "#profile" not in css:
        raise check50.Failure(
            "Missing ID selector '#profile' in active CSS styles",
            help="Style your profile card container using `#profile` selector"
        )
        
    # Check Class selector
    if ".title" not in css:
        raise check50.Failure(
            "Missing class selector '.title' in active CSS styles",
            help="Style your student name heading using `.title` selector"
        )
        
    # Check container properties on ID selector
    for prop in ["width", "max-width", "margin", "padding", "background", "border"]:
        if prop not in css:
            raise check50.Failure(
                f"Missing box model/layout property '{prop}' in active CSS styles"
            )
            
    # Check general styling requirements
    if "color" not in css:
        raise check50.Failure("Missing color declaration in active CSS")
    if "font-family" not in css:
        raise check50.Failure("Missing font-family declaration in active CSS")
    if "font-size" not in css:
        raise check50.Failure("Missing font-size declaration in active CSS")
    if "line-height" not in css:
        raise check50.Failure("Missing line-height declaration in active CSS")
    if "letter-spacing" not in css:
        raise check50.Failure("Missing letter-spacing declaration in active CSS")
    if "text-align" not in css:
        raise check50.Failure("Missing text-align declaration in active CSS")
        
    # Check hover selector
    if "hover" not in css:
        raise check50.Failure(
            "Missing hover state styling (e.g. a:hover)",
            help="Style links on hover using a:hover selector"
        )
    if "text-decoration" not in css:
        raise check50.Failure("Missing text-decoration declaration in hover styles")
