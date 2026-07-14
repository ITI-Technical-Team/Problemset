import check50
import re


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _lower(path):
    return _read(path).lower()


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
    lower = _lower("index.html")
    if "<title" not in lower or "</title>" not in lower:
        raise check50.Failure(
            "Missing <title> element inside <head>",
            help="Add <title>Your Page Title</title> inside the <head> section"
        )


@check50.check(exists)
def has_header_tag():
    """index.html has a <header> element welcoming the visitor"""
    lower = _lower("index.html")
    if "<header" not in lower or "</header>" not in lower:
        raise check50.Failure(
            "Missing <header> element in index.html",
            help="Add a <header>Welcome</header> at the top of <body>"
        )


@check50.check(exists)
def has_two_paragraphs():
    """index.html has at least 2 <p> elements"""
    lower = _lower("index.html")
    paras = re.findall(r'<p[^>]*>(.*?)</p>', lower, re.DOTALL)
    non_empty = [p for p in paras if p.strip()]
    if len(non_empty) < 2:
        raise check50.Failure(
            f"Found {len(non_empty)} non-empty <p> element(s), expected at least 2",
            help="Add at least 2 paragraphs: one about yourself and one emphasized/strong"
        )


@check50.check(exists)
def has_strong():
    """index.html has a <strong> element inside a paragraph"""
    lower = _lower("index.html")
    if "<strong>" not in lower and "<strong " not in lower:
        raise check50.Failure(
            "Missing <strong> element",
            help="Make one of your paragraphs <strong>: <p><strong>text</strong></p>"
        )


@check50.check(exists)
def has_em():
    """index.html has an <em> element inside a paragraph"""
    lower = _lower("index.html")
    if "<em>" not in lower and "<em " not in lower:
        raise check50.Failure(
            "Missing <em> element",
            help="Make one of your paragraphs <em>: <p><em>text</em></p>"
        )


@check50.check(exists)
def has_ul_with_3_items():
    """index.html has a <ul> with at least 3 <li> items (favourite websites)"""
    lower = _lower("index.html")
    if "<ul" not in lower:
        raise check50.Failure(
            "Missing <ul> element",
            help="Add <ul> with 3 favourite learning websites as <li> items"
        )
    ul_match = re.search(r'<ul[^>]*>(.*?)</ul>', lower, re.DOTALL)
    if ul_match:
        li_count = len(re.findall(r'<li[^>]*>', ul_match.group(1)))
        if li_count < 3:
            raise check50.Failure(
                f"Found {li_count} <li> item(s) in <ul>, expected at least 3",
                help="List your top 3 favourite websites for learning web development"
            )


@check50.check(exists)
def has_ol_with_3_items():
    """index.html has an <ol> with at least 3 <li> items (skills)"""
    lower = _lower("index.html")
    if "<ol" not in lower:
        raise check50.Failure(
            "Missing <ol> element",
            help="Add <ol> with at least 3 web development skills as <li> items"
        )
    ol_match = re.search(r'<ol[^>]*>(.*?)</ol>', lower, re.DOTALL)
    if ol_match:
        li_count = len(re.findall(r'<li[^>]*>', ol_match.group(1)))
        if li_count < 3:
            raise check50.Failure(
                f"Found {li_count} <li> item(s) in <ol>, expected at least 3",
                help="List at least 3 skills (e.g. HTML, CSS, JavaScript) in your ordered list"
            )


@check50.check(exists)
def has_figure_with_img_and_figcaption():
    """index.html has a <figure> with <img> and <figcaption>"""
    lower = _lower("index.html")
    if "<figure" not in lower:
        raise check50.Failure(
            "Missing <figure> element",
            help="Wrap your image in <figure><img ...><figcaption>caption</figcaption></figure>"
        )
    if "<figcaption" not in lower:
        raise check50.Failure(
            "Missing <figcaption> inside <figure>",
            help="Add <figcaption>your caption text</figcaption> inside the <figure>"
        )
    if "<img" not in lower:
        raise check50.Failure(
            "Missing <img> inside <figure>",
            help="Add an <img src='...' alt='...'> inside your <figure>"
        )


@check50.check(exists)
def has_google_link():
    """index.html has a hyperlink to google.com"""
    lower = _lower("index.html")
    if "google.com" not in lower:
        raise check50.Failure(
            "Missing hyperlink to google.com",
            help="Add <a href='https://www.google.com'>...</a> in a paragraph or figcaption"
        )


@check50.check(exists)
def has_contact_page_link():
    """index.html links to contact.html"""
    lower = _lower("index.html")
    if "contact.html" not in lower:
        raise check50.Failure(
            "index.html does not link to contact.html",
            help="Add <a href='contact.html'>Contact Me</a> on your index page"
        )


@check50.check(exists)
def has_footer_with_copyright():
    """index.html has a <footer> with a copyright notice"""
    lower = _lower("index.html")
    if "<footer" not in lower:
        raise check50.Failure(
            "Missing <footer> element",
            help="Add <footer>&copy; 2025 Your Name</footer> at the bottom of <body>"
        )
    footer_match = re.search(r'<footer[^>]*>(.*?)</footer>', lower, re.DOTALL)
    if footer_match:
        content = footer_match.group(1)
        if "copyright" not in content and "©" not in content and "&copy;" not in content and "©" not in content:
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
    lower = _lower("contact.html")
    has_phone = bool(re.search(r'\+?\d[\d\s\-]{6,}', lower))
    has_email = "@" in lower
    if not has_phone and not has_email:
        raise check50.Failure(
            "contact.html does not contain a phone number or email address",
            help="Add your phone number and/or email address in contact.html"
        )


@check50.check(exists)
def contact_has_back_link():
    """contact.html has an anchor link back to index.html"""
    lower = _lower("contact.html")
    if "index.html" not in lower:
        raise check50.Failure(
            "contact.html does not link back to index.html",
            help="Add <a href='index.html'>Back to Home</a> in contact.html"
        )
