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


# ─── existence & basic structure ─────────────────────────────────────────────

@check50.check()
def exists():
    """food.html exists"""
    check50.exists("food.html")


@check50.check(exists)
def has_doctype():
    """food.html has <!DOCTYPE html>"""
    raw = _read("food.html")
    # Strip HTML comments so a commented-out DOCTYPE (e.g. <!--<!DOCTYPE html>-->) fails
    uncommented = re.sub(r'<!--.*?-->', '', raw, flags=re.DOTALL)
    if not re.search(r'<!doctype\s+html', uncommented, re.IGNORECASE):
        raise check50.Failure(
            "Missing <!DOCTYPE html> declaration",
            help="The first line of your file must be <!DOCTYPE html>"
        )
    _check_tag_closed("food.html", "html")
    _check_tag_closed("food.html", "head")
    _check_tag_closed("food.html", "body")


@check50.check(exists)
def has_head_body():
    """food.html has <head> and <body>"""
    _check_tag_closed("food.html", "head")
    _check_tag_closed("food.html", "body")
    html = _read("food.html")
    soup = BeautifulSoup(html, "html.parser")
    if not soup.head:
        raise check50.Failure("Missing <head> element", help="Every HTML page needs a <head> block")
    if not soup.body:
        raise check50.Failure("Missing <body> element", help="Every HTML page needs a <body> block")


@check50.check(exists)
def has_title_egyptian_food():
    """<title> reads 'Egyptian Food'"""
    _check_tag_closed("food.html", "title")
    html = _read("food.html")
    soup = BeautifulSoup(html, "html.parser")
    if not soup.title or "egyptian food" not in soup.title.get_text().lower():
        raise check50.Failure(
            "Expected <title>Egyptian Food</title>",
            help="Set your <title> tag text to 'Egyptian Food'"
        )


# ─── header ───────────────────────────────────────────────────────────────────

@check50.check(exists)
def has_header_element():
    """page has a <header> element"""
    _check_tag_closed("food.html", "header")
    _check_tag_closed("food.html", "p")
    html = _read("food.html")
    soup = BeautifulSoup(html, "html.parser")
    if not soup.find("header"):
        raise check50.Failure(
            "Missing <header> element",
            help="Add a <header> at the top of <body> with the page title and subtitle"
        )


@check50.check(has_header_element)
def header_contains_egyptian_food_text():
    """<header> contains a heading (e.g. <h1>) with 'Egyptian Food'"""
    html = _read("food.html")
    soup = BeautifulSoup(html, "html.parser")
    header = soup.find("header")
    
    # Must contain a heading element (h1, h2, h3, etc.)
    heading = header.find(["h1", "h2", "h3", "h4", "h5", "h6"])
    if not heading:
        raise check50.Failure(
            "Missing heading tag inside <header>",
            help="Add a heading tag (like <h1>) inside your <header> element"
        )
        
    if "egyptian food" not in heading.get_text().lower():
        raise check50.Failure(
            f"Heading inside <header> does not contain 'Egyptian Food'",
            help=f"Your heading tag should contain the text 'Egyptian Food'. Found: '{heading.get_text().strip()}'"
        )


@check50.check(has_header_element)
def header_contains_subtitle_paragraph():
    """<header> contains a <p> subtitle"""
    html = _read("food.html")
    soup = BeautifulSoup(html, "html.parser")
    header = soup.find("header")
    if not header.find("p"):
        raise check50.Failure(
            "No <p> subtitle found inside <header>",
            help="Add a <p> subtitle paragraph describing the page inside your <header>"
        )


# ─── table structure ──────────────────────────────────────────────────────────

@check50.check(exists)
def has_table():
    """page has a <table> element"""
    _check_tag_closed("food.html", "table")
    html = _read("food.html")
    soup = BeautifulSoup(html, "html.parser")
    if not soup.find("table"):
        raise check50.Failure(
            "Missing <table> element",
            help="Build your food layout inside a <table>"
        )


@check50.check(has_table)
def has_at_least_3_rows():
    """table has at least 3 <tr> rows"""
    _check_tag_closed("food.html", "tr")
    html = _read("food.html")
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    rows = table.find_all("tr")
    if len(rows) < 3:
        raise check50.Failure(
            f"Found {len(rows)} row(s) in <table>, expected at least 3",
            help="Add at least 3 <tr> rows — one row per food dish"
        )


@check50.check(has_table)
def each_row_has_2_cells():
    """each table row has exactly 2 <td> cells (text + image)"""
    _check_tag_closed("food.html", "td")
    html = _read("food.html")
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    rows = table.find_all("tr")
    for i, row in enumerate(rows):
        cells = row.find_all("td")
        if len(cells) != 2:
            raise check50.Failure(
                f"Row {i+1} has {len(cells)} <td> cell(s), expected 2 (one for text, one for image)",
                help="Each <tr> should have exactly 2 <td> cells: one with <p> text, one with <img>"
            )


@check50.check(has_table)
def has_paragraphs_in_cells():
    """table cells contain <p> text paragraphs"""
    _check_tag_closed("food.html", "p")
    html = _read("food.html")
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    paragraphs = table.find_all("p")
    if len(paragraphs) < 3:
        raise check50.Failure(
            f"Found {len(paragraphs)} <p> element(s) inside the table, expected at least 3",
            help="Add a <p> description paragraph in one <td> of each row"
        )


@check50.check(has_table)
def has_at_least_3_images():
    """table has at least 3 food images"""
    html = _read("food.html")
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    imgs = table.find_all("img")
    
    if len(imgs) < 3:
        raise check50.Failure(
            f"Found {len(imgs)} image(s) inside the table, expected at least 3",
            help="Add an <img> of a food dish in one <td> of each row"
        )
        
    for img in imgs:
        src = img.get("src", "").strip()
        if not src:
            raise check50.Failure(
                "An <img> tag is missing the 'src' attribute",
                help="Make sure all <img> elements specify a source file/URL using src=\"...\""
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


@check50.check(has_table)
def images_have_alt():
    """all <img> elements inside the table have alt attributes"""
    html = _read("food.html")
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    imgs = table.find_all("img")
    for img in imgs:
        if not img.get("alt"):
            # Construct a snippet for the error message
            img_snippet = str(img)[:60]
            raise check50.Failure(
                f"An <img> inside the table is missing the alt attribute: {img_snippet}",
                help="Add alt=\"description of the dish\" to every <img> tag"
            )
