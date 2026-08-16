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


def _find_section(sections, keyword):
    """Find a section by heading text or id attribute."""
    for sec in sections:
        # Check id attribute
        if keyword in (sec.get("id") or "").lower():
            return sec
        # Check heading text
        headings = sec.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        if any(keyword in h.get_text().lower() for h in headings):
            return sec
    return None


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
    """index.html has <header> with name (h1) and job title (p)"""
    _check_tag_closed("index.html", "header")
    _check_tag_closed("index.html", "h1")
    _check_tag_closed("index.html", "p")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    header = soup.find("header")
    if not header:
        raise check50.Failure("Missing <header> element")

    h1 = header.find("h1")
    if not h1 or not h1.get_text().strip():
        raise check50.Failure("Missing or empty <h1> name inside <header>")

    p = header.find("p")
    if not p or not p.get_text().strip():
        raise check50.Failure("Missing or empty <p> job title inside <header>")


@check50.check(has_doctype)
def test_nav():
    """index.html has <nav> containing five links (with href) for Home, About, Skills, Projects, Contact"""
    _check_tag_closed("index.html", "nav")
    _check_tag_closed("index.html", "a")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    nav = soup.find("nav")
    if not nav:
        raise check50.Failure("Missing <nav> element")

    links = nav.find_all("a")
    if len(links) < 5:
        raise check50.Failure(
            f"Found {len(links)} link(s) inside <nav>, expected at least 5",
            help="Add links for Home, About, Skills, Projects, and Contact inside <nav> using <a> tags"
        )

    # Check that every nav link has an href attribute
    for link in links:
        if not link.get("href"):
            raise check50.Failure(
                f"<a> tag with text '{link.get_text().strip()}' inside <nav> is missing an href attribute",
                help="Each <a> tag in your navigation must have an href attribute, e.g. <a href=\"#about\">About</a>"
            )

    text = nav.get_text().lower()
    for word in ["home", "about", "skill", "project", "contact"]:
        if word not in text:
            raise check50.Failure(
                f"Missing link for '{word}' inside <nav>",
                help=f"Make sure to include a link for {word} in your navigation links"
            )


@check50.check(has_doctype)
def test_about_section():
    """index.html has About section with a <div> containing photo, 2 paragraphs, and formatting elements (strong, em, b, i, span, br)"""
    _check_tag_closed("index.html", "section")
    _check_tag_closed("index.html", "div")
    _check_tag_closed("index.html", "strong")
    _check_tag_closed("index.html", "em")
    _check_tag_closed("index.html", "b")
    _check_tag_closed("index.html", "i")
    _check_tag_closed("index.html", "span")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")

    sections = soup.find_all("section")
    if not sections:
        raise check50.Failure("Missing <section> elements")

    about_section = _find_section(sections, "about")
    if not about_section:
        raise check50.Failure(
            "Could not identify About section",
            help="Ensure one of your <section> elements has id='about' or contains an <h2>About</h2> heading"
        )

    div = about_section.find("div")
    if not div:
        raise check50.Failure(
            "Missing <div> element inside the About section",
            help="Wrap the About section contents inside a <div>"
        )

    img = div.find("img")
    if not img:
        raise check50.Failure(
            "Missing <img> inside the About section's <div>"
        )
    src = img.get("src", "").strip()
    if not src:
        raise check50.Failure(
            "The <img> inside About section is missing a src attribute",
            help="Add a src attribute to your <img> tag pointing to your photo, e.g. <img src=\"photo.jpg\" alt=\"My Photo\">"
        )

    paragraphs = div.find_all("p")
    if len(paragraphs) < 2:
        raise check50.Failure(
            f"Found {len(paragraphs)} paragraph(s) in About section's <div>, expected at least 2",
            help="Add at least two paragraphs describing yourself inside the About section's <div>"
        )

    # Check formatting tags
    for tag in ["strong", "em", "b", "i", "span", "br"]:
        if not div.find(tag):
            raise check50.Failure(
                f"Missing <{tag}> tag inside the About section's <div> text"
            )


@check50.check(has_doctype)
def test_skills_section():
    """index.html has Skills section containing <ul> (5 skills) and <ol> (learning steps)"""
    _check_tag_closed("index.html", "ul")
    _check_tag_closed("index.html", "ol")
    _check_tag_closed("index.html", "li")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")

    sections = soup.find_all("section")
    skills_section = _find_section(sections, "skill")
    if not skills_section:
        raise check50.Failure(
            "Could not identify Skills section",
            help="Ensure one of your <section> elements has id='skills' or contains an <h2>Skills</h2> heading"
        )

    ul = skills_section.find("ul")
    if not ul:
        raise check50.Failure("Missing unordered list <ul> inside Skills section")
    ul_items = ul.find_all("li")
    if len(ul_items) < 5:
        raise check50.Failure(
            f"Expected at least 5 skills as <li> items in <ul>, found {len(ul_items)}"
        )

    ol = skills_section.find("ol")
    if not ol:
        raise check50.Failure("Missing ordered list <ol> inside Skills section")
    ol_items = ol.find_all("li")
    if len(ol_items) < 2:
        raise check50.Failure(
            f"Expected steps to become a web developer as <li> items in <ol>, found {len(ol_items)}"
        )


@check50.check(has_doctype)
def test_projects_section():
    """index.html has Projects section containing a table with the specified project statuses and tfoot Total Projects: 3"""
    _check_tag_closed("index.html", "table")
    _check_tag_closed("index.html", "thead")
    _check_tag_closed("index.html", "tbody")
    _check_tag_closed("index.html", "tfoot")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")

    sections = soup.find_all("section")
    proj_section = _find_section(sections, "project")
    if not proj_section:
        raise check50.Failure(
            "Could not identify Projects section",
            help="Ensure one of your <section> elements has id='projects' or contains an <h2>Projects</h2> heading"
        )

    table = proj_section.find("table")
    if not table:
        raise check50.Failure("Missing <table> element inside Projects section")

    thead = table.find("thead")
    if not thead:
        raise check50.Failure("Missing <thead> element inside Projects table")

    # Check that <th> header cells are present and non-empty
    th_cells = thead.find_all("th")
    if not th_cells:
        raise check50.Failure(
            "Missing <th> header cells inside <thead> of Projects table",
            help="Add <th> elements for each column header, e.g. <th>Project</th> <th>Technology</th> <th>Status</th>"
        )
    for th in th_cells:
        if not th.get_text().strip():
            raise check50.Failure(
                "Found an empty <th> header cell in the Projects table's <thead>",
                help="Make sure each <th> contains text, e.g. <th>Project</th>"
            )

    if not table.find("tbody"):
        raise check50.Failure("Missing <tbody> element inside Projects table")
    tfoot = table.find("tfoot")
    if not tfoot:
        raise check50.Failure("Missing <tfoot> element inside Projects table")

    tbody_text = table.find("tbody").get_text().lower()
    for word in ["portfolio", "calculator", "registration form", "completed", "in progress"]:
        if word not in tbody_text:
            raise check50.Failure(
                f"Missing expected project information '{word}' in <tbody>",
                help="Make sure table rows display projects: Portfolio (Completed), Calculator (In Progress), and Registration Form (Completed)"
            )

    tfoot_text = tfoot.get_text().lower()
    if "total projects" not in tfoot_text or "3" not in tfoot_text:
        raise check50.Failure(
            "<tfoot> does not display 'Total Projects: 3'",
            help="Ensure your Projects table footer displays the text 'Total Projects: 3'"
        )


@check50.check(has_doctype)
def test_contact_section():
    """index.html has Contact section containing a <form> with name, email, password, textarea, select (3 options), and submit button"""
    _check_tag_closed("index.html", "form")
    _check_tag_closed("index.html", "label")
    _check_tag_closed("index.html", "textarea")
    _check_tag_closed("index.html", "select")
    _check_tag_closed("index.html", "option")
    _check_tag_closed("index.html", "button")
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")

    sections = soup.find_all("section")
    contact_section = _find_section(sections, "contact")
    if not contact_section:
        raise check50.Failure(
            "Could not identify Contact section",
            help="Ensure one of your <section> elements has id='contact' or contains an <h2>Contact</h2> heading"
        )

    form = contact_section.find("form")
    if not form:
        raise check50.Failure("Missing <form> inside Contact section")

    # Check inputs
    inputs = form.find_all("input")
    types = [inp.get("type", "text").lower() for inp in inputs]
    if "email" not in types:
        raise check50.Failure("Missing <input type=\"email\"> inside contact form")
    if "password" not in types:
        raise check50.Failure("Missing <input type=\"password\"> inside contact form")
    if not any(t == "text" for t in types) and not any(t == "" for t in types):
        raise check50.Failure("Missing <input type=\"text\"> for Name inside contact form")

    # Check textarea
    textarea = form.find("textarea")
    if not textarea:
        raise check50.Failure("Missing <textarea> inside contact form for message")

    # Check select and options
    select = form.find("select")
    if not select:
        raise check50.Failure("Missing <select> inside contact form for department")
    options = [opt.get_text().lower().strip() for opt in select.find_all("option")]
    for opt_word in ["frontend", "backend", "full stack"]:
        opt_found = any(opt_word in o or opt_word.replace(" ", "") in o for o in options)
        if not opt_found:
            raise check50.Failure(
                f"Missing <option> for '{opt_word}' in department select list dropdown"
            )

    # Check labels: must exist, have text, and be linked via for/id
    labels = form.find_all("label")
    if len(labels) < 5:
        raise check50.Failure(
            f"Found {len(labels)} <label> element(s), expected at least 5 (one for each input, textarea, and select)",
            help="Ensure Name, Email, Password, Message, and Department each have their own <label>"
        )
    for label in labels:
        if not label.get_text().strip():
            raise check50.Failure(
                "Found an empty <label> element in the contact form",
                help="Each <label> must contain descriptive text, e.g. <label for=\"name\">Name:</label>"
            )
        for_attr = label.get("for")
        if not for_attr:
            raise check50.Failure(
                f"<label> with text '{label.get_text().strip()}' is missing a 'for' attribute",
                help="Link each <label> to its input using the 'for' attribute matching the input's 'id', e.g. <label for=\"email\">Email:</label>"
            )
        if not form.find(id=for_attr):
            raise check50.Failure(
                f"<label for=\"{for_attr}\"> does not match any element with id=\"{for_attr}\" in the contact form",
                help=f"Add id=\"{for_attr}\" to the input/textarea/select that this label describes"
            )

    # Check submit button
    submit = form.find("button") or form.find("input", type="submit")
    if not submit:
        raise check50.Failure("Missing submit button inside contact form")


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
