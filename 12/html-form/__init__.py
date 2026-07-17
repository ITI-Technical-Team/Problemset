import check50
import re
from bs4 import BeautifulSoup


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


# ─── existence & structure ────────────────────────────────────────────────────

@check50.check()
def exists():
    """register.html exists"""
    check50.exists("register.html")


@check50.check(exists)
def has_doctype():
    """register.html has <!DOCTYPE html>"""
    if not re.search(r'<!doctype\s+html', _read("register.html"), re.IGNORECASE):
        raise check50.Failure(
            "Missing <!DOCTYPE html> declaration",
            help="The first line of register.html must be <!DOCTYPE html>"
        )


@check50.check(exists)
def has_title():
    """<title> reads 'Course Registration'"""
    html = _read("register.html")
    soup = BeautifulSoup(html, "html.parser")
    if not soup.title or "course registration" not in soup.title.get_text().lower():
        raise check50.Failure(
            "Expected <title>Course Registration</title>",
            help="Set your <title> inside <head> to 'Course Registration'"
        )


@check50.check(exists)
def has_form():
    """page has a <form> element"""
    html = _read("register.html")
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
    html = _read("register.html")
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
    html = _read("register.html")
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
    html = _read("register.html")
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
    html = _read("register.html")
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
    html = _read("register.html")
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
    html = _read("register.html")
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
    html = _read("register.html")
    soup = BeautifulSoup(html, "html.parser")
    labels = soup.find_all("label")
    has_repass = any("repassword" in lbl.get_text().lower() for lbl in labels)
    # Check general text if not inside a label tag
    if not has_repass and "repassword" not in html.lower():
        raise check50.Failure(
            "Missing 'Repassword' label",
            help="Add a <label>Repassword :</label> for the confirm-password field"
        )


# ─── radio buttons ────────────────────────────────────────────────────────────

@check50.check(exists)
def has_2_radio_buttons():
    """form has 2 radio buttons for gender (Male / Female)"""
    html = _read("register.html")
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
        
    # Check page text for Male and Female
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
    html = _read("register.html")
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
    html = _read("register.html")
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
    """form has a submit button"""
    html = _read("register.html")
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        raise check50.Failure("Missing <form> element")
        
    # Check for <input type="submit"> or <button type="submit"> or <button> inside form
    has_sub = form.find("input", type=lambda t: t and t.lower() == "submit") or \
              form.find("button", type=lambda t: t and t.lower() == "submit") or \
              form.find("button")
              
    if not has_sub:
        raise check50.Failure(
            "Missing submit button",
            help="Add <input type='submit' value='SUBMIT'> or <button type='submit'>Submit</button>"
        )


@check50.check(exists)
def has_reset_button():
    """form has <input type='reset'> or <button type='reset'>"""
    html = _read("register.html")
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
    html = _read("register.html")
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
