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
    """index.html has <nav> containing at least 3 non-empty anchor links (with href)"""
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

    for link in links:
        if not link.get("href"):
            raise check50.Failure(
                f"<a> tag with text '{link.get_text().strip()}' inside <nav> is missing an 'href' attribute",
                help="Each <a> tag in your navigation must specify a link target using href=\"...\""
            )
        if not link.get_text().strip():
            raise check50.Failure(
                "Found an empty <a> tag inside <nav>",
                help="Each <a> tag inside <nav> must contain visible link text (e.g. <a href=\"#about\">About</a>)"
            )


@check50.check(has_doctype)
def test_about_section():
    """index.html has <section> with a valid <img> and a paragraph containing non-empty strong, em, span, and br elements"""
    _check_tag_closed("index.html", "section")
    _check_tag_closed("index.html", "strong")
    _check_tag_closed("index.html", "em")
    _check_tag_closed("index.html", "span")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    
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
    src = img.get("src", "").strip()
    if not src:
        raise check50.Failure(
            "The <img> tag is missing a 'src' attribute",
            help="Make sure you specify a source file/URL for your <img> tag using src=\"...\""
        )

    # Check that src points to an image file, not a web directory / html page
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

    # Check for paragraph in about section
    p = img_section.find("p")
    if not p or not p.get_text().strip():
        raise check50.Failure(
            "Missing or empty paragraph introducing yourself in the about <section>",
            help="Add a paragraph of text inside the <section> using <p>"
        )
        
    # Check formatting elements inside section
    strong = img_section.find("strong")
    if not strong or not strong.get_text().strip():
        raise check50.Failure(
            "Missing or empty <strong> element in the about section",
            help="Add non-empty text inside <strong> (e.g. <strong>Developer</strong>)"
        )

    em = img_section.find("em")
    if not em or not em.get_text().strip():
        raise check50.Failure(
            "Missing or empty <em> element in the about section",
            help="Add non-empty text inside <em> (e.g. <em>passionate</em>)"
        )

    span = img_section.find("span")
    if not span or not span.get_text().strip():
        raise check50.Failure(
            "Missing or empty <span> element in the about section",
            help="Add non-empty text inside <span>"
        )

    if not img_section.find("br"):
        raise check50.Failure("Missing <br> element in the about section")


@check50.check(has_doctype)
def test_skills_list():
    """index.html has an unordered list (<ul>) with at least 5 non-empty skill items (<li>)"""
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
        
    all_items = ul.find_all("li")
    non_empty_items = [li for li in all_items if li.get_text().strip()]
    if len(non_empty_items) < 5:
        raise check50.Failure(
            f"Found {len(non_empty_items)} non-empty <li> item(s) in <ul>, expected at least 5",
            help="Add at least 5 skills with text inside <li> items inside your <ul> list"
        )


@check50.check(has_doctype)
def test_learning_plan():
    """index.html has an ordered list (<ol>) with at least 4 non-empty learning steps (<li>)"""
    _check_tag_closed("index.html", "ol")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    ol = soup.find("ol")
    if not ol:
        raise check50.Failure(
            "Missing ordered list <ol> for learning steps",
            help="Add an ordered list <ol> to show your learning plan"
        )
        
    all_items = ol.find_all("li")
    non_empty_items = [li for li in all_items if li.get_text().strip()]
    if len(non_empty_items) < 4:
        raise check50.Failure(
            f"Found {len(non_empty_items)} non-empty <li> item(s) in <ol>, expected at least 4",
            help="Add at least 4 learning steps with text inside <li> items inside your <ol> list"
        )


@check50.check(has_doctype)
def test_footer():
    """index.html has a <footer> containing a copyright message with year and name"""
    _check_tag_closed("index.html", "footer")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    footer = soup.find("footer")
    if not footer:
        raise check50.Failure(
            "Missing <footer> element",
            help="Add a <footer> element at the bottom of the body"
        )
        
    text = footer.get_text().strip().lower()
    raw = str(footer).lower()
    has_sym = "copyright" in text or "©" in text or "&copy;" in raw or "&#169;" in raw
    if not has_sym:
        raise check50.Failure(
            "<footer> does not contain a copyright message or copyright symbol (&copy; or ©)",
            help="Add a copyright message inside <footer> using &copy; or © symbol"
        )

    # Check for year (e.g. 2025, 2026)
    has_year = bool(re.search(r'\b(20\d{2}|19\d{2})\b', text))
    if not has_year:
        raise check50.Failure(
            "<footer> is missing the copyright year (e.g. 2026)",
            help="Include the year inside your <footer>, e.g. &copy; 2026 Your Name"
        )

    # Remove symbol & year to check for name/holder text
    clean_text = re.sub(r'copyright|©|&copy;|&#169;|20\d{2}|19\d{2}', '', text).strip()
    if len(clean_text) < 2:
        raise check50.Failure(
            "<footer> is missing your name or copyright holder text",
            help="Include your name inside <footer>, e.g. &copy; 2026 Your Name"
        )
