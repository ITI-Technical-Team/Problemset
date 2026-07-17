import check50
import re
from bs4 import BeautifulSoup


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


# ─── existence & basic structure ─────────────────────────────────────────────

@check50.check()
def exists():
    """food.html exists"""
    check50.exists("food.html")


@check50.check(exists)
def has_doctype():
    """food.html has <!DOCTYPE html>"""
    if not re.search(r'<!doctype\s+html', _read("food.html"), re.IGNORECASE):
        raise check50.Failure(
            "Missing <!DOCTYPE html> declaration",
            help="The first line of your file must be <!DOCTYPE html>"
        )


@check50.check(exists)
def has_head_body():
    """food.html has <head> and <body>"""
    html = _read("food.html")
    soup = BeautifulSoup(html, "html.parser")
    if not soup.head:
        raise check50.Failure("Missing <head> element", help="Every HTML page needs a <head> block")
    if not soup.body:
        raise check50.Failure("Missing <body> element", help="Every HTML page needs a <body> block")


@check50.check(exists)
def has_title_egyptian_food():
    """<title> reads 'Egyptian Food'"""
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
