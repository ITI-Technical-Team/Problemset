import check50
import re
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
    _check_tag_closed("index.html", "html")
    _check_tag_closed("index.html", "head")
    _check_tag_closed("index.html", "body")


@check50.check(has_doctype)
def test_header():
    """index.html has <header> containing a <h1> and a <p> welcome paragraph"""
    _check_tag_closed("index.html", "header")
    _check_tag_closed("index.html", "h1")
    _check_tag_closed("index.html", "p")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    header = soup.find("header")
    if not header:
        raise check50.Failure("Missing <header> element in index.html")
    
    h1 = header.find("h1")
    if not h1 or not h1.get_text().strip():
        raise check50.Failure(
            "Missing or empty <h1> title inside <header>",
            help="Add a main title inside <header> using <h1> tag"
        )
        
    p = header.find("p")
    if not p or not p.get_text().strip():
        raise check50.Failure(
            "Missing or empty welcome paragraph <p> inside <header>",
            help="Add a short welcome message inside <header> using <p> tag"
        )


@check50.check(has_doctype)
def test_nav():
    """index.html has <nav> containing at least 3 anchor links"""
    _check_tag_closed("index.html", "nav")
    _check_tag_closed("index.html", "a")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    nav = soup.find("nav")
    if not nav:
        raise check50.Failure("Missing <nav> element in index.html")
        
    links = nav.find_all("a")
    if len(links) < 3:
        raise check50.Failure(
            f"Found {len(links)} link(s) inside <nav>, expected at least 3",
            help="Add at least 3 links (e.g. Home, About, Contact) inside <nav> using <a> tags"
        )


@check50.check(has_doctype)
def test_about_section():
    """index.html has <section> with an <img> and a paragraph containing strong, em, span, and br elements"""
    _check_tag_closed("index.html", "section")
    _check_tag_closed("index.html", "strong")
    _check_tag_closed("index.html", "em")
    _check_tag_closed("index.html", "span")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    
    # Try to find a section that contains an img, or any section
    sections = soup.find_all("section")
    if not sections:
        raise check50.Failure("Missing <section> element in index.html")
        
    img_section = None
    for sec in sections:
        if sec.find("img"):
            img_section = sec
            break
            
    if not img_section:
        raise check50.Failure(
            "None of the <section> elements contain an <img> tag",
            help="Add your photo inside a <section> using <img> tag"
        )
        
    img = img_section.find("img")
    if not img.get("src", "").strip():
        raise check50.Failure(
            "The <img> tag is missing a 'src' attribute",
            help="Make sure you specify a source file/URL for your <img> tag using src=\"...\""
        )
        
    # Check for formatting elements in the section or its paragraphs
    p = img_section.find("p")
    if not p:
        raise check50.Failure(
            "Missing paragraph introducing yourself in the about <section>",
            help="Add a paragraph of text inside the <section> using <p>"
        )
        
    # Check formatting elements
    if not img_section.find("strong"):
        raise check50.Failure("Missing <strong> element in the about section")
    if not img_section.find("em"):
        raise check50.Failure("Missing <em> element in the about section")
    if not img_section.find("span"):
        raise check50.Failure("Missing <span> element in the about section")
    if not img_section.find("br"):
        raise check50.Failure("Missing <br> element in the about section")


@check50.check(has_doctype)
def test_skills_list():
    """index.html has an unordered list (<ul>) with at least 5 skill items (<li>)"""
    _check_tag_closed("index.html", "ul")
    _check_tag_closed("index.html", "li")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    ul = soup.find("ul")
    if not ul:
        raise check50.Failure(
            "Missing unordered list <ul> for skills",
            help="Add an unordered list <ul> to present your skills"
        )
        
    items = ul.find_all("li")
    if len(items) < 5:
        raise check50.Failure(
            f"Found {len(items)} item(s) in the unordered list, expected at least 5",
            help="Add at least 5 skills as <li> items inside your <ul> list"
        )


@check50.check(has_doctype)
def test_learning_plan():
    """index.html has an ordered list (<ol>) with at least 4 learning steps (<li>)"""
    _check_tag_closed("index.html", "ol")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    ol = soup.find("ol")
    if not ol:
        raise check50.Failure(
            "Missing ordered list <ol> for learning steps",
            help="Add an ordered list <ol> to show your learning plan"
        )
        
    items = ol.find_all("li")
    if len(items) < 4:
        raise check50.Failure(
            f"Found {len(items)} item(s) in the ordered list, expected at least 4",
            help="Add at least 4 learning steps as <li> items inside your <ol> list"
        )


@check50.check(has_doctype)
def test_footer():
    """index.html has a <footer> containing copyright message"""
    _check_tag_closed("index.html", "footer")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    footer = soup.find("footer")
    if not footer:
        raise check50.Failure(
            "Missing <footer> element",
            help="Add a <footer> element at the bottom of the body"
        )
    text = footer.get_text().lower()
    raw = str(footer).lower()
    has_sym = "copyright" in text or "©" in text or "&copy;" in raw or "&#169;" in raw
    if not has_sym:
        raise check50.Failure(
            "<footer> does not contain a copyright message or copyright symbol (&copy; or ©)"
        )
