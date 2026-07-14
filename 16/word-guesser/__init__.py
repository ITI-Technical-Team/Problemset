import check50
import re


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _html():
    return _read("index.html").lower()


# ─── existence & structure ────────────────────────────────────────────────────

@check50.check()
def exists():
    """index.html exists"""
    check50.exists("index.html")


@check50.check(exists)
def has_dashboard_inputs():
    """index.html has nameInput, preview element, moodSelect, showBtn, message, and quote elements"""
    html = _html()
    
    # nameInput
    if 'id="nameinput"' not in html and "id='nameinput'" not in html:
        raise check50.Failure("Missing input with id='nameInput'")
        
    # preview
    if 'id="preview"' not in html and "id='preview'" not in html:
        raise check50.Failure("Missing element with id='preview'")
        
    # moodSelect
    if 'id="moodselect"' not in html and "id='moodselect'" not in html:
         raise check50.Failure("Missing select with id='moodSelect'")
    for opt in ["happy", "sad", "excited"]:
        if opt not in html:
            raise check50.Failure(f"Missing mood select option '{opt.capitalize()}'")
            
    # showBtn
    if 'id="showbtn"' not in html and "id='showbtn'" not in html:
         raise check50.Failure("Missing button with id='showBtn'")
         
    # message & quote
    if 'id="message"' not in html and "id='message'" not in html:
         raise check50.Failure("Missing element with id='message'")
    if 'id="quote"' not in html and "id='quote'" not in html:
         raise check50.Failure("Missing element with id='quote'")


# ─── JS checks ────────────────────────────────────────────────────────────────

@check50.check(exists)
def contains_mood_quotes():
    """JavaScript defines quotes object categorized by Happy, Sad, and Excited moods"""
    html = _read("index.html").lower()
    for mood in ["happy", "sad", "excited"]:
        if mood not in html:
            raise check50.Failure(
                f"Missing quotes category or quotes for mood '{mood.capitalize()}'",
                help=f"Make sure to group quotes by mood: let quotes = {{ {mood.capitalize()}: [...] }}"
            )


@check50.check(exists)
def has_keyup_listener():
    """JavaScript listens for keyup events on nameInput to update preview"""
    html = _read("index.html").lower()
    if "keyup" not in html:
        raise check50.Failure(
            "Missing keyup event listener",
            help="Add a keyup event listener on the nameInput element to show live typing preview"
        )
    if "typing:" not in html:
        raise check50.Failure(
            "Live typing preview doesn't show 'Typing: [name]'",
            help="Update preview.textContent = 'Typing: ' + nameInput.value inside the keyup handler"
        )


@check50.check(exists)
def has_click_listener():
    """JavaScript listens for click events on showBtn"""
    html = _read("index.html").lower()
    if "click" not in html:
        raise check50.Failure(
            "Missing click event listener on the Show button",
            help="Add a click event listener: showBtn.addEventListener('click', ...)"
        )


@check50.check(exists)
def performs_validation():
    """showBtn click handler validates name length (at least 3 characters)"""
    html = _read("index.html").lower()
    if "length" not in html or "3" not in html:
        raise check50.Failure(
            "Missing name length validation",
            help="Check if name length is less than 3, e.g. name.length < 3"
        )
    if "at least 3 letters" not in html and "at least 3 characters" not in html:
        raise check50.Failure(
            "Missing validation alert message",
            help="Show alert('Please enter a valid name with at least 3 letters.') when name is too short"
        )


@check50.check(exists)
def sets_dynamic_styles():
    """showBtn click handler changes background and text colors based on selected mood"""
    html = _read("index.html").lower()
    # Check for color hexes
    colors = ["#d4edda", "#f8d7da", "#fff3cd"]
    for color in colors:
        if color not in html:
            raise check50.Failure(
                f"Missing background color update for category: {color}",
                help=f"Set body.style.backgroundColor = '{color}' inside the showBtn click handler"
            )
            
    # Check if style.color is modified
    if "style.color" not in html:
        raise check50.Failure(
            "Does not update greeting text color based on mood",
            help="Set message.style.color based on the selected mood"
        )
