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
    """index.html has <header> displaying the academy name"""
    _check_tag_closed("index.html", "header")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    header = soup.find("header")
    if not header or not header.get_text().strip():
        raise check50.Failure(
            "Missing or empty <header> element in index.html",
            help="Add a <header> element showing the name of your academy"
        )


@check50.check(has_doctype)
def test_nav():
    """index.html has <nav> containing links (with href) to Home, Courses, and Register"""
    _check_tag_closed("index.html", "nav")
    _check_tag_closed("index.html", "a")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    nav = soup.find("nav")
    if not nav:
        raise check50.Failure("Missing <nav> element")

    links = nav.find_all("a")
    if len(links) < 3:
        raise check50.Failure(
            f"Found {len(links)} link(s) inside <nav>, expected at least 3",
            help="Add links for Home, Courses, and Register inside <nav> using <a> tags"
        )

    # Check that links have href attributes
    for link in links:
        if not link.get("href"):
            raise check50.Failure(
                f"<a> tag with text '{link.get_text().strip()}' inside <nav> is missing an href attribute",
                help="Each <a> tag in your navigation must have an href attribute, e.g. <a href=\"#courses\">Courses</a>"
            )

    text = nav.get_text().lower()
    for link_word in ["home", "course", "register"]:
        if link_word not in text:
            raise check50.Failure(
                f"Missing link for '{link_word}' inside <nav>",
                help=f"Make sure to include a link for {link_word} in your navigation links"
            )


@check50.check(has_doctype)
def test_table():
    """index.html has a <table> with courses details including duration and foot showing Total Courses: 3"""
    _check_tag_closed("index.html", "table")
    _check_tag_closed("index.html", "thead")
    _check_tag_closed("index.html", "tbody")
    _check_tag_closed("index.html", "tfoot")
    _check_tag_closed("index.html", "tr")
    _check_tag_closed("index.html", "th")
    _check_tag_closed("index.html", "td")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        raise check50.Failure("Missing <table> element")

    thead = table.find("thead")
    if not thead:
        raise check50.Failure("Missing <thead> element inside <table>")

    # Check that <th> cells in the header are non-empty
    th_cells = thead.find_all("th")
    if not th_cells:
        raise check50.Failure(
            "Missing <th> header cells inside <thead>",
            help="Add <th> elements inside <thead> to label your table columns (e.g. Course, Duration)"
        )
    for th in th_cells:
        if not th.get_text().strip():
            raise check50.Failure(
                "Found an empty <th> header cell in <thead>",
                help="Make sure each <th> contains text to label the column (e.g. <th>Course</th>)"
            )

    if not table.find("tbody"):
        raise check50.Failure("Missing <tbody> element inside <table>")

    tfoot = table.find("tfoot")
    if not tfoot:
        raise check50.Failure("Missing <tfoot> element inside <table>")

    # Check course and duration names in table
    tbody_text = table.find("tbody").get_text()
    for word in ["html", "css", "javascript", "2 weeks", "3 weeks", "5 weeks"]:
        if word not in tbody_text.lower():
            raise check50.Failure(
                f"Missing or incorrect course/duration info '{word}' in <tbody>",
                help="Make sure your table rows contain HTML, CSS, JavaScript, and their respective durations"
            )

    # Check total courses in footer
    tfoot_text = tfoot.get_text().lower()
    if "total courses" not in tfoot_text or "3" not in tfoot_text:
        raise check50.Failure(
            "<tfoot> does not display 'Total Courses: 3'",
            help="Ensure your table footer displays the text 'Total Courses: 3'"
        )


@check50.check(has_doctype)
def test_form():
    """index.html has a <form> containing name, email, password, feedback/goals textarea, department select, and a submit button"""
    _check_tag_closed("index.html", "form")
    _check_tag_closed("index.html", "label")
    _check_tag_closed("index.html", "textarea")
    _check_tag_closed("index.html", "select")
    _check_tag_closed("index.html", "option")
    _check_tag_closed("index.html", "button")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        raise check50.Failure("Missing <form> element")

    # Check inputs
    inputs = form.find_all("input")
    types = [inp.get("type", "text").lower() for inp in inputs]
    if "email" not in types:
        raise check50.Failure("Missing <input type=\"email\"> inside registration form")
    if "password" not in types:
        raise check50.Failure("Missing <input type=\"password\"> inside registration form")
    if not any(t == "text" for t in types) and not any(t == "" for t in types):
        raise check50.Failure("Missing <input type=\"text\"> for Name inside registration form")

    # Check textarea
    textarea = form.find("textarea")
    if not textarea:
        raise check50.Failure(
            "Missing <textarea> inside registration form for feedback/goals"
        )

    # Check select and options
    select = form.find("select")
    if not select:
        raise check50.Failure("Missing <select> inside registration form for department")
    options = [opt.get_text().lower().strip() for opt in select.find_all("option")]
    for opt_word in ["frontend", "backend", "full stack"]:
        opt_found = any(opt_word in o or opt_word.replace(" ", "") in o for o in options)
        if not opt_found:
            raise check50.Failure(
                f"Missing <option> for '{opt_word}' in department select list",
                help="Make sure department select dropdown includes: Frontend, Backend, and Full Stack options"
            )

    # Check labels: must exist, have text, and be linked to inputs via for/id
    labels = form.find_all("label")
    if len(labels) < 5:
        raise check50.Failure(
            f"Found {len(labels)} <label> element(s), expected at least 5 (one for each input, textarea, and select)",
            help="Ensure Name, Email, Password, Feedback/Goals, and Department each have their own <label>"
        )
    for label in labels:
        if not label.get_text().strip():
            raise check50.Failure(
                "Found an empty <label> element in the form",
                help="Each <label> must contain descriptive text, e.g. <label for=\"name\">Name:</label>"
            )
        for_attr = label.get("for")
        if not for_attr:
            raise check50.Failure(
                f"<label> with text '{label.get_text().strip()}' is missing a 'for' attribute",
                help="Link each <label> to its input using the 'for' attribute matching the input's 'id', e.g. <label for=\"email\">Email:</label>"
            )
        # Check that there is an element with matching id in the form
        if not form.find(id=for_attr):
            raise check50.Failure(
                f"<label for=\"{for_attr}\"> does not match any element with id=\"{for_attr}\" in the form",
                help=f"Add id=\"{for_attr}\" to the input/textarea/select that this label describes"
            )

    # Check submit button
    submit = form.find("button") or form.find("input", type="submit")
    if not submit:
        raise check50.Failure(
            "Missing submit button inside form",
            help="Add a submit button inside your <form> using <button type=\"submit\">Submit</button>"
        )


@check50.check(has_doctype)
def test_footer():
    """index.html has a <footer> with a copyright message"""
    _check_tag_closed("index.html", "footer")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    footer = soup.find("footer")
    if not footer:
        raise check50.Failure("Missing <footer> element")
    text = footer.get_text().lower()
    raw = str(footer).lower()
    has_sym = "copyright" in text or "©" in text or "&copy;" in raw or "&#169;" in raw
    if not has_sym:
        raise check50.Failure(
            "<footer> does not contain a copyright message or copyright symbol (&copy; or ©)"
        )
