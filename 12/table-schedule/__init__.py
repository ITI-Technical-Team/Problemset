import check50
import re


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _lower(path):
    return _read(path).lower()


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
    lower = _lower("food.html")
    for tag in ["<head", "<body"]:
        if tag not in lower:
            raise check50.Failure(
                f"Missing {tag}> element",
                help="Every HTML page needs <head> and <body>"
            )


@check50.check(exists)
def has_title_egyptian_food():
    """<title> reads 'Egyptian Food'"""
    lower = _lower("food.html")
    match = re.search(r'<title[^>]*>(.*?)</title>', lower, re.DOTALL)
    if not match or "egyptian food" not in match.group(1):
        raise check50.Failure(
            "Expected <title>Egyptian Food</title>",
            help="Set your <title> tag to 'Egyptian Food'"
        )


# ─── header ───────────────────────────────────────────────────────────────────

@check50.check(exists)
def has_header_element():
    """page has a <header> element"""
    lower = _lower("food.html")
    if "<header" not in lower:
        raise check50.Failure(
            "Missing <header> element",
            help="Add a <header> at the top of <body> with the page title and subtitle"
        )


@check50.check(has_header_element)
def header_contains_egyptian_food_text():
    """<header> contains 'Egyptian Food' text"""
    lower = _lower("food.html")
    header_match = re.search(r'<header[^>]*>(.*?)</header>', lower, re.DOTALL)
    if not header_match or "egyptian food" not in header_match.group(1):
        raise check50.Failure(
            "'Egyptian Food' heading not found inside <header>",
            help="Add a heading (<h1> or similar) with 'Egyptian Food' inside your <header>"
        )


@check50.check(has_header_element)
def header_contains_subtitle_paragraph():
    """<header> contains a <p> subtitle"""
    lower = _lower("food.html")
    header_match = re.search(r'<header[^>]*>(.*?)</header>', lower, re.DOTALL)
    if not header_match or "<p" not in header_match.group(1):
        raise check50.Failure(
            "No <p> subtitle found inside <header>",
            help="Add a <p>These are the most famous Egyptian food dishes</p> inside the <header>"
        )


# ─── table structure ──────────────────────────────────────────────────────────

@check50.check(exists)
def has_table():
    """page has a <table> element"""
    if "<table" not in _lower("food.html"):
        raise check50.Failure(
            "Missing <table> element",
            help="Build your food layout inside a <table>"
        )


@check50.check(has_table)
def has_at_least_3_rows():
    """table has at least 3 <tr> rows"""
    lower = _lower("food.html")
    table_match = re.search(r'<table[^>]*>(.*?)</table>', lower, re.DOTALL)
    if not table_match:
        raise check50.Failure("Could not parse <table> element")
    tr_count = len(re.findall(r'<tr[^>]*>', table_match.group(1)))
    if tr_count < 3:
        raise check50.Failure(
            f"Found {tr_count} row(s) in <table>, expected at least 3",
            help="Add at least 3 <tr> rows — one row per food dish"
        )


@check50.check(has_table)
def each_row_has_2_cells():
    """each table row has exactly 2 <td> cells (text + image)"""
    lower = _lower("food.html")
    table_match = re.search(r'<table[^>]*>(.*?)</table>', lower, re.DOTALL)
    if not table_match:
        return
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_match.group(1), re.DOTALL)
    for i, row in enumerate(rows):
        td_count = len(re.findall(r'<td[^>]*>', row))
        if td_count < 2:
            raise check50.Failure(
                f"Row {i+1} has {td_count} <td> cell(s), expected 2 (one for text, one for image)",
                help="Each <tr> should have exactly 2 <td> cells: one with <p> text, one with <img>"
            )


@check50.check(has_table)
def has_paragraphs_in_cells():
    """table cells contain <p> text paragraphs"""
    lower = _lower("food.html")
    table_match = re.search(r'<table[^>]*>(.*?)</table>', lower, re.DOTALL)
    if not table_match:
        return
    p_count = len(re.findall(r'<p[^>]*>', table_match.group(1)))
    if p_count < 3:
        raise check50.Failure(
            f"Found {p_count} <p> element(s) inside the table, expected at least 3",
            help="Add a <p> description paragraph in one <td> of each row"
        )


@check50.check(has_table)
def has_at_least_3_images():
    """table has at least 3 food images"""
    lower = _lower("food.html")
    table_match = re.search(r'<table[^>]*>(.*?)</table>', lower, re.DOTALL)
    if not table_match:
        return
    img_count = len(re.findall(r'<img[^>]*>', table_match.group(1)))
    if img_count < 3:
        raise check50.Failure(
            f"Found {img_count} image(s) inside the table, expected at least 3",
            help="Add an <img> of a food dish in one <td> of each row (at least 3 rows)"
        )


@check50.check(has_table)
def images_have_alt():
    """all <img> elements inside the table have alt attributes"""
    lower = _lower("food.html")
    table_match = re.search(r'<table[^>]*>(.*?)</table>', lower, re.DOTALL)
    if not table_match:
        return
    imgs = re.findall(r'<img[^>]*>', table_match.group(1))
    for img in imgs:
        if "alt=" not in img:
            raise check50.Failure(
                f"An <img> inside the table is missing the alt attribute: {img[:60]}",
                help="Add alt='description of the dish' to every <img> tag"
            )
