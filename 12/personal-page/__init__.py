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
    raw = _read("index.html")
    # Strip HTML comments so a commented-out DOCTYPE fails
    uncommented = re.sub(r'<!--.*?-->', '', raw, flags=re.DOTALL)
    if not re.search(r'<!doctype\s+html', uncommented, re.IGNORECASE):
        raise check50.Failure(
            "Missing <!DOCTYPE html> declaration in index.html",
            help="The first line of every HTML5 file must be <!DOCTYPE html>"
        )
    _check_tag_closed("index.html", "html")
    _check_tag_closed("index.html", "head")
    _check_tag_closed("index.html", "body")


@check50.check(exists)
def has_title():
    """index.html has a <title> inside <head>"""
    _check_tag_closed("index.html", "title")
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
    _check_tag_closed("index.html", "header")
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
    _check_tag_closed("index.html", "p")
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
    _check_tag_closed("index.html", "strong")
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
    _check_tag_closed("index.html", "em")
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
    _check_tag_closed("index.html", "ul")
    _check_tag_closed("index.html", "li")
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

    # Check if the list is misplaced (e.g. preceded by a heading that specifies "skills" instead of "websites")
    prev_heading = ul.find_previous(["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span"])
    if prev_heading:
        text = prev_heading.get_text().lower()
        if "skill" in text or "develop" in text or "know" in text or "lang" in text or "مهار" in text:
            raise check50.Failure(
                "Your list of web development skills must be an ordered list (<ol>), not an unordered list (<ul>)",
                help="Change your skills list tag from <ul> to <ol> and your websites list tag from <ol> to <ul>"
            )


@check50.check(exists)
def has_ol_with_3_items():
    """index.html has an <ol> with at least 3 <li> items (skills)"""
    _check_tag_closed("index.html", "ol")
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

    # Check if the list is misplaced (e.g. preceded by a heading that specifies "websites" instead of "skills")
    prev_heading = ol.find_previous(["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span"])
    if prev_heading:
        text = prev_heading.get_text().lower()
        if "website" in text or "site" in text or "link" in text or "favorite" in text or "favourite" in text or "موقع" in text or "مواقع" in text or "رابط" in text or "روابط" in text:
            raise check50.Failure(
                "Your list of favourite websites must be an unordered list (<ul>), not an ordered list (<ol>)",
                help="Change your favourite websites list tag from <ol> to <ul> and your skills list tag from <ul> to <ol>"
            )


@check50.check(exists)
def has_figure_with_img_and_figcaption():
    """index.html has a <figure> with <img> and <figcaption>"""
    _check_tag_closed("index.html", "figure")
    _check_tag_closed("index.html", "figcaption")
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
        
    src = img.get("src", "").strip()
    if not src:
        raise check50.Failure(
            "The <img> tag inside <figure> is missing a 'src' attribute",
            help="Make sure your <img> element specifies a source file/URL using src=\"...\""
        )
    # Check if remote link is broken
    if src.startswith("http://") or src.startswith("https://"):
        import urllib.request
        import urllib.error
        try:
            req = urllib.request.Request(
                src, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=2.0) as response:
                pass
        except urllib.error.HTTPError as e:
            raise check50.Failure(
                f"Referenced remote image URL '{src}' is broken (returned HTTP error {e.code})",
                help="Make sure the image URL is correct and active"
            )
        except Exception:
            # Ignore connection/timeout errors to allow offline grading
            pass
    elif src.startswith("data:"):
        pass
    else:
        # Local image: verify it has a valid image extension to ensure it is not dummy text
        valid_exts = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp")
        if not any(src.lower().endswith(ext) for ext in valid_exts):
            raise check50.Failure(
                f"Referenced image path '{src}' is not a valid image file",
                help="Make sure your src attribute points to a valid image file (ending with .png, .jpg, .jpeg, etc.)"
            )


@check50.check(exists)
def has_google_link():
    """index.html has a hyperlink to google.com"""
    _check_tag_closed("index.html", "a")
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
    _check_tag_closed("index.html", "a")
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
    _check_tag_closed("index.html", "footer")
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
    raw = _read("contact.html")
    # Strip HTML comments so a commented-out DOCTYPE fails
    uncommented = re.sub(r'<!--.*?-->', '', raw, flags=re.DOTALL)
    if not re.search(r'<!doctype\s+html', uncommented, re.IGNORECASE):
        raise check50.Failure(
            "Missing <!DOCTYPE html> in contact.html",
            help="Add <!DOCTYPE html> as the first line of contact.html"
        )
    _check_tag_closed("contact.html", "html")
    _check_tag_closed("contact.html", "head")
    _check_tag_closed("contact.html", "body")


@check50.check(exists)
def contact_has_phone_or_email():
    """contact.html contains a phone number or email address"""
    _check_tag_closed("contact.html", "p")
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
    _check_tag_closed("contact.html", "a")
    html = _read("contact.html")
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a")
    has_back = any((link.get("href") or "").strip() == "index.html" for link in links)
    if not has_back:
        raise check50.Failure(
            "contact.html does not link back to index.html",
            help="Add <a href='index.html'>Back to Home</a> in contact.html"
        )
