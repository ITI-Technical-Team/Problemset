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
    """index.html contains required elements (div with id='profile', img, h1 with class='title', p, ol, link)"""
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
    if not img or not img.get("src", "").strip():
        raise check50.Failure("Missing <img> or missing src attribute inside profile card")
        
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
    items = ol.find_all("li")
    if len(items) < 2:
        raise check50.Failure(
            f"Found {len(items)} item(s) in ordered list, expected at least 2",
            help="Add your learning goals inside the <ol> list using <li> items"
        )
        
    link = profile.find("a")
    if not link or not link.get("href", "").strip():
        raise check50.Failure("Missing portfolio link <a> inside profile card")


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
        
    css = style.get_text().lower()
    
    # Check ID selector
    if "#profile" not in css:
        raise check50.Failure(
            "Missing ID selector '#profile' in CSS styles",
            help="Style your profile card container using `#profile` selector"
        )
        
    # Check Class selector
    if ".title" not in css:
        raise check50.Failure(
            "Missing class selector '.title' in CSS styles",
            help="Style your student name heading using `.title` selector"
        )
        
    # Check container properties on ID selector
    for prop in ["width", "max-width", "margin", "padding", "background", "border"]:
        if prop not in css:
            raise check50.Failure(
                f"Missing box model/layout property '{prop}' in CSS styles"
            )
            
    # Check general styling requirements
    if "color" not in css:
        raise check50.Failure("Missing color declaration")
    if "font-family" not in css:
        raise check50.Failure("Missing font-family declaration")
    if "font-size" not in css:
        raise check50.Failure("Missing font-size declaration")
    if "line-height" not in css:
        raise check50.Failure("Missing line-height declaration")
    if "letter-spacing" not in css:
        raise check50.Failure("Missing letter-spacing declaration")
    if "text-align" not in css:
        raise check50.Failure("Missing text-align declaration")
        
    # Check hover selector
    if "hover" not in css:
        raise check50.Failure(
            "Missing hover state styling (e.g. a:hover)",
            help="Style links on hover using a:hover selector"
        )
    if "text-decoration" not in css:
        raise check50.Failure("Missing text-decoration declaration in hover styles")
