import check50
import re
from bs4 import BeautifulSoup


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


# ══════════════════════════════════════════════════════════
#  index.html checks
# ══════════════════════════════════════════════════════════

@check50.check()
def exists():
    """index.html and contact.html exist"""
    check50.exists("index.html")
    check50.exists("contact.html")


@check50.check(exists)
def has_doctype():
    """index.html has <!DOCTYPE html>"""
    if not re.search(r'<!doctype\s+html', _read("index.html"), re.IGNORECASE):
        raise check50.Failure(
            "Missing <!DOCTYPE html> declaration in index.html",
            help="The first line of every HTML5 file must be <!DOCTYPE html>"
        )


@check50.check(exists)
def has_title():
    """index.html has a <title> inside <head>"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    if not soup.title or not soup.title.get_text().strip():
        raise check50.Failure(
            "Missing <title> element inside <head>",
            help="Add a `<title>Your Page Title</title>` inside the `<head>` section of index.html"
        )


@check50.check(exists)
def has_header_tag():
    """index.html has a <header> element welcoming the visitor"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    if not soup.find("header"):
        raise check50.Failure(
            "Missing <header> element in index.html",
            help="Add a `<header>Welcome</header>` inside your `<body>` tag"
        )


@check50.check(exists)
def has_two_paragraphs():
    """index.html has at least 2 non-empty <p> elements"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    paragraphs = soup.find_all("p")
    non_empty = [p for p in paragraphs if p.get_text().strip()]
    if len(non_empty) < 2:
        raise check50.Failure(
            f"Found {len(non_empty)} non-empty <p> element(s), expected at least 2",
            help="Add at least 2 paragraphs: one about yourself and one emphasized/strong"
        )


@check50.check(exists)
def has_strong():
    """index.html has a <strong> element"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    if not soup.find("strong"):
        raise check50.Failure(
            "Missing <strong> element",
            help="Make one of your paragraphs <strong>: <p><strong>text</strong></p>"
        )


@check50.check(exists)
def has_em():
    """index.html has an <em> element"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    if not soup.find("em"):
        raise check50.Failure(
            "Missing <em> element",
            help="Make one of your paragraphs <em>: <p><em>text</em></p>"
        )


@check50.check(exists)
def has_ul_with_3_items():
    """index.html has a <ul> with at least 3 <li> items (favourite websites)"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    ul = soup.find("ul")
    if not ul:
        raise check50.Failure(
            "Missing <ul> element",
            help="Add a `<ul>` list containing your top 3 favourite learning websites as `<li>` items"
        )
    items = ul.find_all("li")
    if len(items) < 3:
        raise check50.Failure(
            f"Found {len(items)} <li> item(s) in <ul>, expected at least 3",
            help="Add at least 3 <li> items inside your <ul> list"
        )


@check50.check(exists)
def has_ol_with_3_items():
    """index.html has an <ol> with at least 3 <li> items (skills)"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    ol = soup.find("ol")
    if not ol:
        raise check50.Failure(
            "Missing <ol> element",
            help="Add a `<ol>` list containing at least 3 of your web development skills as `<li>` items"
        )
    items = ol.find_all("li")
    if len(items) < 3:
        raise check50.Failure(
            f"Found {len(items)} <li> item(s) in <ol>, expected at least 3",
            help="Add at least 3 <li> items inside your <ol> list"
        )


@check50.check(exists)
def has_figure_with_img_and_figcaption():
    """index.html has a <figure> with <img> and <figcaption> and referenced files exist"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    figure = soup.find("figure")
    if not figure:
        raise check50.Failure(
            "Missing <figure> element",
            help="Wrap your image in <figure><img src='...' alt='...'><figcaption>caption</figcaption></figure>"
        )
    img = figure.find("img")
    if not img:
        raise check50.Failure(
            "Missing <img> inside <figure>",
            help="Add an <img src='...' alt='...'> inside your <figure>"
        )
    figcaption = figure.find("figcaption")
    if not figcaption:
        raise check50.Failure(
            "Missing <figcaption> inside <figure>",
            help="Add a <figcaption>caption</figcaption> inside your <figure>"
        )
        
    # Check that referenced local image file actually exists
    src = img.get("src", "").strip()
    if not src:
        raise check50.Failure(
            "The <img> tag inside <figure> is missing a 'src' attribute",
            help="Make sure your <img> element specifies a source file/URL using src=\"...\""
        )
    if not (src.startswith("http://") or src.startswith("https://") or src.startswith("data:")):
        try:
            check50.exists(src)
        except check50.Failure:
            raise check50.Failure(
                f"Referenced image file '{src}' does not exist in your directory",
                help=f"Make sure you have placed the image file '{src}' in the same directory as index.html"
            )


@check50.check(exists)
def has_google_link():
    """index.html has a hyperlink to google.com"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a")
    has_google = any("google.com" in (link.get("href") or "").lower() for link in links)
    if not has_google:
        raise check50.Failure(
            "Missing hyperlink to google.com",
            help="Add <a href='https://www.google.com'>...</a> in a paragraph or figcaption"
        )


@check50.check(exists)
def has_contact_page_link():
    """index.html links to contact.html"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a")
    has_contact = any((link.get("href") or "").strip() == "contact.html" for link in links)
    if not has_contact:
        raise check50.Failure(
            "index.html does not link to contact.html",
            help="Add <a href='contact.html'>Contact Me</a> on your index page"
        )


@check50.check(exists)
def has_footer_with_copyright():
    """index.html has a <footer> with a copyright notice"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    footer = soup.find("footer")
    if not footer:
        raise check50.Failure(
            "Missing <footer> element",
            help="Add a <footer>&copy; 2025 Your Name</footer> at the bottom of <body>"
        )
    text = footer.get_text().lower()
    if "copyright" not in text and "©" not in text and "&copy;" not in text and "©" not in text:
        raise check50.Failure(
            "<footer> does not contain a copyright notice",
            help="Add &copy; or the © symbol inside your <footer>"
        )


# ══════════════════════════════════════════════════════════
#  contact.html checks
# ══════════════════════════════════════════════════════════

@check50.check(exists)
def contact_has_doctype():
    """contact.html has <!DOCTYPE html>"""
    if not re.search(r'<!doctype\s+html', _read("contact.html"), re.IGNORECASE):
        raise check50.Failure(
            "Missing <!DOCTYPE html> in contact.html",
            help="Add <!DOCTYPE html> as the first line of contact.html"
        )


@check50.check(exists)
def contact_has_phone_or_email():
    """contact.html contains a phone number or email address"""
    html = _read("contact.html")
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text().lower()
    
    has_phone = bool(re.search(r'\+?\d[\d\s\-]{6,}', text))
    has_email = "@" in text
    
    if not has_phone and not has_email:
        raise check50.Failure(
            "contact.html does not contain a phone number or email address",
            help="Add your phone number and/or email address in contact.html"
        )


@check50.check(exists)
def contact_has_back_link():
    """contact.html has an anchor link back to index.html"""
    html = _read("contact.html")
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a")
    has_back = any((link.get("href") or "").strip() == "index.html" for link in links)
    if not has_back:
        raise check50.Failure(
            "contact.html does not link back to index.html",
            help="Add <a href='index.html'>Back to Home</a> in contact.html"
        )
