import check50
import re
from bs4 import BeautifulSoup


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _uncommented_html(path="register.html"):
    raw = _read(path)
    return re.sub(r"<!--.*?-->", "", raw, flags=re.DOTALL)


def _check_tag_closed(filename, tag):
    clean_html = _uncommented_html(filename)
    open_count = len(re.findall(rf"<{tag}\b", clean_html, re.IGNORECASE))
    close_count = len(re.findall(rf"</{tag}\s*>", clean_html, re.IGNORECASE))
    if open_count > close_count:
        raise check50.Failure(
            f"Unclosed <{tag}> tag in {filename}",
            help=f"Make sure you close every <{tag}> tag with a matching </{tag}> tag"
        )


# ─── existence & structure ────────────────────────────────────────────────────

@check50.check()
def exists():
    """register.html exists"""
    check50.exists("register.html")


@check50.check(exists)
def has_doctype():
    """register.html has <!DOCTYPE html>"""
    uncommented = _uncommented_html("register.html")
    if not re.search(r'<!doctype\s+html', uncommented, re.IGNORECASE):
        raise check50.Failure(
            "Missing <!DOCTYPE html> declaration",
            help="The first line of register.html must be <!DOCTYPE html>"
        )
    _check_tag_closed("register.html", "html")
    _check_tag_closed("register.html", "head")
    _check_tag_closed("register.html", "body")


@check50.check(exists)
def has_title():
    """<title> reads 'Course Registration'"""
    _check_tag_closed("register.html", "title")
    html = _uncommented_html("register.html")
    soup = BeautifulSoup(html, "html.parser")
    if not soup.title or "course registration" not in soup.title.get_text().lower():
        raise check50.Failure(
            "Expected <title>Course Registration</title>",
            help="Set your <title> inside <head> to 'Course Registration'"
        )


@check50.check(exists)
def has_form():
    """page has a <form> element"""
    _check_tag_closed("register.html", "form")
    html = _uncommented_html("register.html")
    soup = BeautifulSoup(html, "html.parser")
    if not soup.find("form"):
        raise check50.Failure(
            "Missing <form> element",
            help="Wrap all your inputs inside a <form> tag"
        )


# ─── fieldset ─────────────────────────────────────────────────────────────────

@check50.check(exists)
def has_fieldset():
    """form has a <fieldset> element (required!)"""
    _check_tag_closed("register.html", "fieldset")
    html = _uncommented_html("register.html")
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form or not form.find("fieldset"):
        raise check50.Failure(
            "Missing <fieldset> element — this is a required tag for this task",
            help="Wrap your form fields in <fieldset><legend>Personal Data</legend>...</fieldset>"
        )


@check50.check(has_fieldset)
def has_legend():
    """<fieldset> has a <legend>"""
    _check_tag_closed("register.html", "legend")
    html = _uncommented_html("register.html")
    soup = BeautifulSoup(html, "html.parser")
    fieldset = soup.find("fieldset")
    legend = fieldset.find("legend") if fieldset else None
    if not legend:
        raise check50.Failure(
            "Missing <legend> inside <fieldset>",
            help="Add <legend>Personal Data</legend> as the first child of <fieldset>"
        )
    if not legend.get_text().strip():
        raise check50.Failure(
            "<legend> is empty — it should say 'Personal Data'",
            help="Set <legend>Personal Data</legend>"
        )


# ─── text inputs ──────────────────────────────────────────────────────────────

@check50.check(exists)
def has_first_name_input():
    """form has a text input for First Name with placeholder"""
    html = _uncommented_html("register.html")
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        raise check50.Failure("Missing <form> element")

    text_inputs = form.find_all("input", type=lambda t: t and t.lower() == "text")
    if not text_inputs:
        raise check50.Failure(
            "Missing <input type='text'> for First Name",
            help="Add <input type='text' placeholder='ex: ahmed'> for the first name"
        )

    has_placeholder = any(inp.get("placeholder") for inp in text_inputs)
    if not has_placeholder:
        raise check50.Failure(
            "Text inputs are missing placeholder attributes",
            help="Add placeholder='ex: ahmed' to the First Name input"
        )


@check50.check(exists)
def has_multiple_text_inputs():
    """form has at least 3 text inputs (first name, second name, phone)"""
    html = _uncommented_html("register.html")
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        raise check50.Failure("Missing <form> element")

    text_inputs = form.find_all("input", type=lambda t: t and t.lower() == "text")
    if len(text_inputs) < 3:
        raise check50.Failure(
            f"Found {len(text_inputs)} <input type='text'> element(s), expected at least 3",
            help="Add text inputs for: First Name, Second Name, and Phone"
        )


@check50.check(exists)
def has_email_input():
    """form has <input type='email'>"""
    html = _uncommented_html("register.html")
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form or not form.find("input", type=lambda t: t and t.lower() == "email"):
        raise check50.Failure(
            "Missing <input type='email'>",
            help="Add <input type='email'> for the Email field"
        )


# ─── password inputs ──────────────────────────────────────────────────────────

@check50.check(exists)
def has_two_password_inputs():
    """form has 2 <input type='password'> (password + repassword)"""
    html = _uncommented_html("register.html")
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        raise check50.Failure("Missing <form> element")

    passwords = form.find_all("input", type=lambda t: t and t.lower() == "password")
    if len(passwords) < 2:
        raise check50.Failure(
            f"Found {len(passwords)} <input type='password'>, expected at least 2 (Password + Repassword)",
            help="Add two password inputs: one for Password and one for Repassword"
        )


@check50.check(exists)
def has_repassword_label():
    """form has a label for Repassword"""
    _check_tag_closed("register.html", "label")
    html = _uncommented_html("register.html")
    soup = BeautifulSoup(html, "html.parser")
    labels = soup.find_all("label")
    has_repass = any("repassword" in lbl.get_text().lower() for lbl in labels)
    if not has_repass and "repassword" not in html.lower():
        raise check50.Failure(
            "Missing 'Repassword' label",
            help="Add a <label>Repassword :</label> for the confirm-password field"
        )


# ─── radio buttons ────────────────────────────────────────────────────────────

@check50.check(exists)
def has_2_radio_buttons():
    """form has 2 radio buttons for gender (Male / Female)"""
    html = _uncommented_html("register.html")
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        raise check50.Failure("Missing <form> element")

    radios = form.find_all("input", type=lambda t: t and t.lower() == "radio")
    if len(radios) < 2:
        raise check50.Failure(
            f"Found {len(radios)} radio button(s), expected at least 2 (Male, Female)",
            help="Add <input type='radio' name='gender' value='male'> Male and <input type='radio' name='gender' value='female'> Female"
        )

    names = set(r.get("name", "").strip().lower() for r in radios)
    names.discard("")
    if len(names) > 1:
        raise check50.Failure(
            f"Radio buttons have different name attributes ({', '.join(sorted(names))}). They must all share the same name to form a group.",
            help="Set the same name (e.g. name='gender') on ALL gender radio buttons"
        )

    text_content = soup.get_text().lower()
    if "male" not in text_content or "female" not in text_content:
        raise check50.Failure(
            "Radio buttons should be labelled 'Male' and 'Female'",
            help="Add labels 'Male' and 'Female' next to each radio button"
        )


# ─── checkboxes ───────────────────────────────────────────────────────────────

@check50.check(exists)
def has_checkboxes():
    """form has at least 2 checkboxes (Student, Graduated)"""
    html = _uncommented_html("register.html")
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        raise check50.Failure("Missing <form> element")

    checkboxes = form.find_all("input", type=lambda t: t and t.lower() == "checkbox")
    if len(checkboxes) < 2:
        raise check50.Failure(
            f"Found {len(checkboxes)} checkbox(es), expected at least 2 (Student, Graduated)",
            help="Add <input type='checkbox'> for 'Student' and 'Graduated'"
        )

    text_content = soup.get_text().lower()
    if "student" not in text_content or "graduated" not in text_content:
        raise check50.Failure(
            "Checkboxes should be labelled 'Student' and 'Graduated'",
            help="Add labels 'Student' and 'Graduated' next to each checkbox"
        )


# ─── select ───────────────────────────────────────────────────────────────────

@check50.check(exists)
def has_select_with_options():
    """form has a <select> drop-down with at least 3 <option> items (university)"""
    _check_tag_closed("register.html", "select")
    _check_tag_closed("register.html", "option")
    html = _uncommented_html("register.html")
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        raise check50.Failure("Missing <form> element")

    select = form.find("select")
    if not select:
        raise check50.Failure(
            "Missing <select> element for university",
            help="Add a <select> drop-down for choosing a university (e.g. AUC, Cairo, Ain Shams)"
        )

    options = select.find_all("option")
    if len(options) < 3:
        raise check50.Failure(
            f"Found {len(options)} <option>(s), expected at least 3",
            help="Add at least 3 university options inside <select>"
        )


# ─── submit & reset buttons ───────────────────────────────────────────────────

@check50.check(exists)
def has_submit_button():
    """form has <input type="submit" value="SUBMIT">"""
    _check_tag_closed("register.html", "button")
    html = _uncommented_html("register.html")
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        raise check50.Failure("Missing <form> element")

    submit_input = form.find("input", type=lambda t: t and t.lower() == "submit")
    if not submit_input:
        raise check50.Failure(
            "Missing <input type=\"submit\"> button",
            help="Use <input type='submit' value='SUBMIT'> — a plain <button> element is not accepted here"
        )

    value = (submit_input.get("value") or "").strip()
    if value.upper() != "SUBMIT":
        raise check50.Failure(
            f"Submit button value is '{value}', expected 'SUBMIT'",
            help="Set value=\"SUBMIT\" on your <input type='submit'> element"
        )


@check50.check(exists)
def has_reset_button():
    """form has <input type='reset'> or <button type='reset'>"""
    _check_tag_closed("register.html", "button")
    html = _uncommented_html("register.html")
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        raise check50.Failure("Missing <form> element")

    has_res = form.find("input", type=lambda t: t and t.lower() == "reset") or \
              form.find("button", type=lambda t: t and t.lower() == "reset")

    if not has_res:
        raise check50.Failure(
            "Missing reset button — a reset option is required",
            help="Add <input type='reset' value='RESET'> or <button type='reset'>Reset</button> next to your submit button"
        )


# ─── labels ───────────────────────────────────────────────────────────────────

@check50.check(exists)
def has_labels():
    """form has <label> elements for its inputs"""
    _check_tag_closed("register.html", "label")
    html = _uncommented_html("register.html")
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        raise check50.Failure("Missing <form> element")

    labels = form.find_all("label")
    if len(labels) < 4:
        raise check50.Failure(
            f"Found {len(labels)} <label>(s), expected at least 4",
            help="Add <label> elements for First Name, Second Name, Phone, Email, Password, etc."
        )
