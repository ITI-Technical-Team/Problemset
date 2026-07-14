import check50
import re


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _lower(path):
    return _read(path).lower()


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
    lower = _lower("register.html")
    match = re.search(r'<title[^>]*>(.*?)</title>', lower, re.DOTALL)
    if not match or "course registration" not in match.group(1):
        raise check50.Failure(
            "Expected <title>Course Registration</title>",
            help="Set your <title> inside <head> to 'Course Registration'"
        )


@check50.check(exists)
def has_form():
    """page has a <form> element"""
    if "<form" not in _lower("register.html"):
        raise check50.Failure(
            "Missing <form> element",
            help="Wrap all your inputs inside a <form> tag"
        )


# ─── fieldset (Task 3 requirement — explicitly highlighted) ───────────────────

@check50.check(exists)
def has_fieldset():
    """form has a <fieldset> element (required!)"""
    lower = _lower("register.html")
    if "<fieldset" not in lower:
        raise check50.Failure(
            "Missing <fieldset> element — this is a required tag for this task",
            help="Wrap your form fields in <fieldset><legend>Personal Data</legend>...</fieldset>"
        )


@check50.check(has_fieldset)
def has_legend():
    """<fieldset> has a <legend>"""
    lower = _lower("register.html")
    fieldset_match = re.search(r'<fieldset[^>]*>(.*?)</fieldset>', lower, re.DOTALL)
    if not fieldset_match or "<legend" not in fieldset_match.group(1):
        raise check50.Failure(
            "Missing <legend> inside <fieldset>",
            help="Add <legend>Personal Data</legend> as the first child of <fieldset>"
        )
    legend_match = re.search(r'<legend[^>]*>(.*?)</legend>', fieldset_match.group(1), re.DOTALL)
    if not legend_match or not legend_match.group(1).strip():
        raise check50.Failure(
            "<legend> is empty — it should say 'Personal Data'",
            help="Set <legend>Personal Data</legend>"
        )


# ─── text inputs ──────────────────────────────────────────────────────────────

@check50.check(exists)
def has_first_name_input():
    """form has a text input for First Name with placeholder"""
    lower = _lower("register.html")
    text_inputs = re.findall(r'<input[^>]+type=["\']?text["\']?[^>]*>', lower)
    if not text_inputs:
        raise check50.Failure(
            "Missing <input type='text'> for First Name",
            help="Add <input type='text' placeholder='ex: ahmed'> for the first name"
        )
    # Check that at least one has a placeholder
    has_placeholder = any("placeholder" in inp for inp in text_inputs)
    if not has_placeholder:
        raise check50.Failure(
            "Text inputs are missing placeholder attributes",
            help="Add placeholder='ex: ahmed' to the First Name input"
        )


@check50.check(exists)
def has_multiple_text_inputs():
    """form has at least 3 text inputs (first name, second name, phone)"""
    lower = _lower("register.html")
    text_inputs = re.findall(r'<input[^>]+type=["\']?text["\']?[^>]*>', lower)
    if len(text_inputs) < 3:
        raise check50.Failure(
            f"Found {len(text_inputs)} <input type='text'> element(s), expected at least 3",
            help="Add text inputs for: First Name, Second Name, and Phone"
        )


@check50.check(exists)
def has_email_input():
    """form has <input type='email'>"""
    if not re.search(r'<input[^>]+type=["\']?email["\']?', _lower("register.html")):
        raise check50.Failure(
            "Missing <input type='email'>",
            help="Add <input type='email'> for the Email field"
        )


# ─── password inputs ──────────────────────────────────────────────────────────

@check50.check(exists)
def has_two_password_inputs():
    """form has 2 <input type='password'> (password + repassword)"""
    lower = _lower("register.html")
    passwords = re.findall(r'<input[^>]+type=["\']?password["\']?', lower)
    if len(passwords) < 2:
        raise check50.Failure(
            f"Found {len(passwords)} <input type='password'>, expected 2 (Password + Repassword)",
            help="Add two password inputs: one for Password and one for Repassword"
        )


@check50.check(exists)
def has_repassword_label():
    """form has a label for Repassword"""
    lower = _lower("register.html")
    if "repassword" not in lower:
        raise check50.Failure(
            "Missing 'Repassword' label",
            help="Add a <label>Repassword :</label> for the confirm-password field"
        )


# ─── radio buttons ────────────────────────────────────────────────────────────

@check50.check(exists)
def has_2_radio_buttons():
    """form has 2 radio buttons for gender (Male / Female)"""
    lower = _lower("register.html")
    radios = re.findall(r'<input[^>]+type=["\']?radio["\']?[^>]*>', lower)
    if len(radios) < 2:
        raise check50.Failure(
            f"Found {len(radios)} radio button(s), expected 2 (Male, Female)",
            help="Add <input type='radio' name='gender' value='male'> Male and <input type='radio' name='gender' value='female'> Female"
        )
    if "male" not in lower or "female" not in lower:
        raise check50.Failure(
            "Radio buttons should be labelled 'Male' and 'Female'",
            help="Add labels 'Male' and 'Female' next to each radio button"
        )


# ─── checkboxes ───────────────────────────────────────────────────────────────

@check50.check(exists)
def has_checkboxes():
    """form has at least 2 checkboxes (Student, Graduated)"""
    lower = _lower("register.html")
    checkboxes = re.findall(r'<input[^>]+type=["\']?checkbox["\']?[^>]*>', lower)
    if len(checkboxes) < 2:
        raise check50.Failure(
            f"Found {len(checkboxes)} checkbox(es), expected at least 2 (Student, Graduated)",
            help="Add <input type='checkbox'> for 'Student' and 'Graduated'"
        )
    if "student" not in lower or "graduated" not in lower:
        raise check50.Failure(
            "Checkboxes should be labelled 'Student' and 'Graduated'",
            help="Add labels 'Student' and 'Graduated' next to each checkbox"
        )


# ─── select ───────────────────────────────────────────────────────────────────

@check50.check(exists)
def has_select_with_options():
    """form has a <select> drop-down with at least 3 <option> items (university)"""
    lower = _lower("register.html")
    if "<select" not in lower:
        raise check50.Failure(
            "Missing <select> element for university",
            help="Add a <select> drop-down for choosing a university (e.g. AUC, Cairo, Ain Shams)"
        )
    option_count = len(re.findall(r'<option[^>]*>', lower))
    if option_count < 3:
        raise check50.Failure(
            f"Found {option_count} <option>(s), expected at least 3",
            help="Add at least 3 university options inside <select>"
        )


# ─── submit & reset buttons ───────────────────────────────────────────────────

@check50.check(exists)
def has_submit_button():
    """form has <input type='submit'>"""
    lower = _lower("register.html")
    if not re.search(r'<input[^>]+type=["\']?submit["\']?', lower) and \
       not re.search(r'<button[^>]+type=["\']?submit["\']?', lower):
        raise check50.Failure(
            "Missing submit button",
            help="Add <input type='submit' value='SUBMIT'>"
        )


@check50.check(exists)
def has_reset_button():
    """form has <input type='reset'>"""
    lower = _lower("register.html")
    if not re.search(r'<input[^>]+type=["\']?reset["\']?', lower) and \
       not re.search(r'<button[^>]+type=["\']?reset["\']?', lower):
        raise check50.Failure(
            "Missing reset button — <input type='reset'> is required",
            help="Add <input type='reset' value='RESET'> next to your submit button"
        )


# ─── labels ───────────────────────────────────────────────────────────────────

@check50.check(exists)
def has_labels():
    """form has <label> elements for its inputs"""
    lower = _lower("register.html")
    label_count = len(re.findall(r'<label[^>]*>', lower))
    if label_count < 4:
        raise check50.Failure(
            f"Found {label_count} <label>(s), expected at least 4",
            help="Add <label> elements for First Name, Second Name, Phone, Email, Password, etc."
        )
