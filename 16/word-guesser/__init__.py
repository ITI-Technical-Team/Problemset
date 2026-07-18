import check50
import re
import subprocess
from bs4 import BeautifulSoup


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _strip_js_comments(code):
    code = re.sub(r'//[^\n]*', '', code)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    return code


# ─── existence & structure ────────────────────────────────────────────────────

@check50.check()
def exists():
    """index.html exists"""
    check50.exists("index.html")


@check50.check(exists)
def has_dashboard_inputs():
    """index.html has nameInput, preview element, moodSelect, showBtn, message, and quote elements"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    
    # nameInput
    if not soup.find(id="nameInput"):
        raise check50.Failure("Missing input with id='nameInput'")
        
    # preview
    if not soup.find(id="preview"):
        raise check50.Failure("Missing element with id='preview'")
        
    # moodSelect
    select = soup.find(id="moodSelect")
    if not select:
         raise check50.Failure("Missing select with id='moodSelect'")
         
    # Check options case-insensitively
    options = [opt.get_text().strip().lower() for opt in select.find_all("option")]
    for opt in ["happy", "sad", "excited"]:
        if not any(opt in o for o in options):
            raise check50.Failure(f"Missing mood select option '{opt.capitalize()}'")
            
    # showBtn
    if not soup.find(id="showBtn"):
         raise check50.Failure("Missing button with id='showBtn'")
         
    # message & quote
    if not soup.find(id="message"):
         raise check50.Failure("Missing element with id='message'")
    if not soup.find(id="quote"):
         raise check50.Failure("Missing element with id='quote'")


# ─── JS checks — functional execution ────────────────────────────────────────

@check50.check(has_dashboard_inputs)
def verifies_dashboard_logic():
    """JavaScript implements mood quotes, keyup live preview, input validation, and mood styling correctly"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script")
    if not script:
        raise check50.Failure("Missing <script> tag")
        
    js_code = script.string or ""
    js_clean = _strip_js_comments(js_code)

    # Active code method existence check
    for item in ["addeventlistener", "keyup", "click", "length", "style.backgroundcolor", "style.color"]:
        if item not in js_clean.lower().replace(" ", ""):
            raise check50.Failure(
                f"Missing required logic/listener: '{item}'",
                help=f"Make sure to implement event listeners and style changes as specified in the task description"
            )

    # Enforce querySelector usage — getElementById is not allowed
    if "getelementbyid" in js_clean.lower().replace(" ", ""):
        raise check50.Failure(
            "getElementById is not allowed",
            help="The task requires using querySelector to select all DOM elements. Replace getElementById with querySelector, e.g. document.querySelector('#nameInput')"
        )
    if "queryselector" not in js_clean.lower().replace(" ", ""):
        raise check50.Failure(
            "Missing querySelector usage",
            help="Use querySelector to select all DOM elements, e.g. document.querySelector('#nameInput')"
        )

    # Node environment setup to mock DOM querySelector, events, alert, styling, and Math.random()
    mock_env = r"""
let _nameInputVal = "";
let _moodSelectVal = "Happy";
let _previewText = "";
let _messageHtml = "";
let _quoteText = "";
let _bodyBg = "";
let _messageColor = "";
let alerted = null;
let _messageUsedInnerHTML = false;

let eventListeners = {};

class MockElement {
    constructor(id) {
        this.id = id;
        this.style = {};
    }
    
    get value() {
        if (this.id === "nameInput") return _nameInputVal;
        if (this.id === "moodSelect") return _moodSelectVal;
        return "";
    }
    set value(v) {
        if (this.id === "nameInput") _nameInputVal = v;
        if (this.id === "moodSelect") _moodSelectVal = v;
    }
    
    get textContent() {
        if (this.id === "preview") return _previewText;
        if (this.id === "quote") return _quoteText;
        if (this.id === "message") return _messageHtml;
        return "";
    }
    set textContent(v) {
        if (this.id === "preview") _previewText = v;
        if (this.id === "quote") _quoteText = v;
        if (this.id === "message") { _messageHtml = v; _messageUsedInnerHTML = false; }
    }
    
    get innerHTML() {
        if (this.id === "message") return _messageHtml;
        return this.textContent;
    }
    set innerHTML(v) {
        if (this.id === "message") { _messageHtml = v; _messageUsedInnerHTML = true; }
        else this.textContent = v;
    }
    
    addEventListener(event, callback) {
        eventListeners[this.id + "_" + event] = callback;
    }
}

let mockBody = {
    style: {
        get backgroundColor() { return _bodyBg; },
        set backgroundColor(v) { _bodyBg = v; }
    }
};

let elements = {
    nameInput: new MockElement("nameInput"),
    moodSelect: new MockElement("moodSelect"),
    preview: new MockElement("preview"),
    message: new MockElement("message"),
    quote: new MockElement("quote"),
    showBtn: new MockElement("showBtn")
};

global.alert = (msg) => { alerted = String(msg); };
global.document = {
    body: mockBody,
    querySelector: (sel) => {
        sel = sel.replace(/[#.]/g, "").trim();
        if (sel === "body") return mockBody;
        return elements[sel] || null;
    }
};
"""

    test_harness = r"""
// 1. Verify quotes object exists and categorizes moods
if (typeof quotes === "undefined") {
    console.log("FAIL_NO_QUOTES");
    process.exit(1);
}
for (const mood of ["Happy", "Sad", "Excited"]) {
    if (!quotes[mood] && !quotes[mood.toLowerCase()]) {
        console.log("FAIL_MOOD_QUOTES_MISSING:" + mood);
        process.exit(1);
    }
}

// 2. Verify event listeners were registered
if (!eventListeners["nameInput_keyup"]) {
    console.log("FAIL_NO_KEYUP_LISTENER");
    process.exit(1);
}
if (!eventListeners["showBtn_click"]) {
    console.log("FAIL_NO_CLICK_LISTENER");
    process.exit(1);
}

// 3. Test keyup listener
// Empty value -> clear preview
_nameInputVal = "   ";
eventListeners["nameInput_keyup"]();
if (_previewText !== "") {
    console.log("FAIL_KEYUP_EMPTY:" + _previewText);
    process.exit(1);
}
// Non-empty value -> Typing: [name]
_nameInputVal = "Mazen";
eventListeners["nameInput_keyup"]();
if (!_previewText.toLowerCase().includes("typing:") || !_previewText.toLowerCase().includes("mazen")) {
    console.log("FAIL_KEYUP_PREVIEW:" + _previewText);
    process.exit(1);
}

// 4. Test click listener validation (length < 3)
_nameInputVal = "Ma";
alerted = null;
eventListeners["showBtn_click"]();
if (alerted === null) {
    console.log("FAIL_NO_VALIDATION_ALERT");
    process.exit(1);
}
if (!alerted.toLowerCase().includes("at least 3")) {
    console.log("FAIL_VALIDATION_ALERT_TEXT:" + alerted);
    process.exit(1);
}

// Boundary test: exactly 3-char name should be ACCEPTED (not alert)
// This catches <= 3 instead of < 3
_nameInputVal = "Ali";
alerted = null;
eventListeners["showBtn_click"]();
if (alerted !== null) {
    console.log("FAIL_VALIDATION_BOUNDARY:" + alerted);
    process.exit(1);
}

// Clear outputs to test valid click
_messageHtml = "";
_quoteText = "";
alerted = null;

// 5. Test Happy Mood
_nameInputVal = "Mazen";
_moodSelectVal = "Happy";
elements.message.style = {}; // reset style
eventListeners["showBtn_click"]();

if (!_messageHtml.toLowerCase().includes("hello") || !_messageHtml.toLowerCase().includes("mazen") || !_messageHtml.toLowerCase().includes("happy")) {
    console.log("FAIL_HAPPY_GREETING:" + _messageHtml);
    process.exit(1);
}
// Check that innerHTML was used (not textContent) for bold rendering
if (!_messageUsedInnerHTML) {
    console.log("FAIL_TEXTCONTENT_USED:" + _messageHtml);
    process.exit(1);
}
// Check for bold formatting on name and mood
if (!_messageHtml.toLowerCase().includes("strong") && !_messageHtml.toLowerCase().includes("b>")) {
    console.log("FAIL_HAPPY_BOLD:" + _messageHtml);
    process.exit(1);
}
if (!_quoteText || _quoteText === '""') {
    console.log("FAIL_HAPPY_QUOTE:" + _quoteText);
    process.exit(1);
}
if (_bodyBg !== "#d4edda") {
    console.log("FAIL_HAPPY_BG:" + _bodyBg);
    process.exit(1);
}
if (elements.message.style.color !== "#155724") {
    console.log("FAIL_HAPPY_COLOR:" + elements.message.style.color);
    process.exit(1);
}

// 6. Test Sad Mood
_bodyBg = "";
elements.message.style = {};
_moodSelectVal = "Sad";
eventListeners["showBtn_click"]();
if (_bodyBg !== "#f8d7da") {
    console.log("FAIL_SAD_BG:" + _bodyBg);
    process.exit(1);
}
if (elements.message.style.color !== "#721c24") {
    console.log("FAIL_SAD_COLOR:" + elements.message.style.color);
    process.exit(1);
}

// 7. Test Excited Mood
_bodyBg = "";
elements.message.style = {};
_moodSelectVal = "Excited";
eventListeners["showBtn_click"]();
if (_bodyBg !== "#fff3cd") {
    console.log("FAIL_EXCITED_BG:" + _bodyBg);
    process.exit(1);
}
if (elements.message.style.color !== "#856404") {
    console.log("FAIL_EXCITED_COLOR:" + elements.message.style.color);
    process.exit(1);
}

console.log("PASS");
"""

    full_js = mock_env + js_code + test_harness

    try:
        res = subprocess.run(["node", "-e", full_js], capture_output=True, text=True)
    except FileNotFoundError:
        return

    if res.returncode != 0:
        out = res.stdout.strip() or res.stderr.strip()
        if out.startswith("FAIL_NO_QUOTES"):
            raise check50.Failure(
                "Missing 'quotes' variable",
                help="Declare a quotes object containing Happy, Sad, and Excited lists"
            )
        elif out.startswith("FAIL_MOOD_QUOTES_MISSING"):
            mood = out.split(":", 1)[1]
            raise check50.Failure(
                f"Missing quotes category or quotes for mood '{mood}'",
                help=f"Make sure to group quotes by mood: let quotes = {{ {mood}: [...] }}"
            )
        elif out.startswith("FAIL_NO_KEYUP_LISTENER"):
            raise check50.Failure(
                "Missing keyup event listener on the nameInput",
                help="Add a keyup listener: nameInput.addEventListener('keyup', ...)"
            )
        elif out.startswith("FAIL_NO_CLICK_LISTENER"):
            raise check50.Failure(
                "Missing click event listener on the Show button",
                help="Add a click listener: showBtn.addEventListener('click', ...)"
            )
        elif out.startswith("FAIL_KEYUP_EMPTY"):
            raise check50.Failure(
                "Live typing preview does not clear when input is empty",
                help="Inside the keyup handler, if value.trim() is empty, set preview.textContent = ''"
            )
        elif out.startswith("FAIL_KEYUP_PREVIEW"):
            got = out.split(":", 1)[1]
            raise check50.Failure(
                "Live typing preview text is incorrect",
                help=f"Expected preview to contain 'Typing: Mazen'. Got: {got!r}"
            )
        elif out.startswith("FAIL_NO_VALIDATION_ALERT"):
            raise check50.Failure(
                "Missing name length validation",
                help="On showBtn click, check if the name length is less than 3, and alert the user"
            )
        elif out.startswith("FAIL_VALIDATION_ALERT_TEXT"):
            got = out.split(":", 1)[1]
            raise check50.Failure(
                "Validation alert message is incorrect",
                help=f"Expected alert to contain 'at least 3 letters' or similar message. Got: {got!r}"
            )
        elif out.startswith("FAIL_VALIDATION_BOUNDARY"):
            raise check50.Failure(
                "Validation condition is too strict: a 3-character name should be accepted",
                help="Use 'name.length < 3' (strictly less than 3), not 'name.length <= 3'. A name like 'Ali' (3 letters) is valid."
            )
        elif out.startswith("FAIL_HAPPY_GREETING"):
            got = out.split(":", 1)[1]
            raise check50.Failure(
                "Greeting message format is incorrect for Happy mood",
                help=f"Expected greeting like 'Hello Mazen! You seem Happy today'. Got: {got!r}"
            )
        elif out.startswith("FAIL_TEXTCONTENT_USED"):
            got = out.split(":", 1)[1]
            raise check50.Failure(
                "Used textContent instead of innerHTML for the greeting message",
                help=f"Use message.innerHTML to set HTML content with bold tags (e.g. <strong>). Using textContent renders HTML tags as literal text. Got: {got!r}"
            )
        elif out.startswith("FAIL_HAPPY_BOLD"):
            got = out.split(":", 1)[1]
            raise check50.Failure(
                "Greeting message is missing bold formatting",
                help="Make the name and mood bold inside the message using <strong> or <b> tags"
            )
        elif out.startswith("FAIL_HAPPY_QUOTE"):
            raise check50.Failure(
                "Mood quote was not displayed inside quotes",
                help="Pick a random quote from the selected mood and set quote.textContent = '\"' + selectedQuote + '\"'"
            )
        elif out.startswith("FAIL_HAPPY_BG") or out.startswith("FAIL_SAD_BG") or out.startswith("FAIL_EXCITED_BG"):
            got = out.split(":", 1)[1]
            raise check50.Failure(
                "Incorrect background color applied based on mood",
                help=f"Verify body background color hex values: Happy (#d4edda), Sad (#f8d7da), Excited (#fff3cd). Got: {got!r}"
            )
        elif out.startswith("FAIL_HAPPY_COLOR") or out.startswith("FAIL_SAD_COLOR") or out.startswith("FAIL_EXCITED_COLOR"):
            got = out.split(":", 1)[1]
            raise check50.Failure(
                "Incorrect greeting text color applied based on mood",
                help=f"Verify message text color hex values: Happy (#155724), Sad (#721c24), Excited (#856404). Got: {got!r}"
            )
        elif out.startswith("ERROR"):
            raise check50.Failure(
                "JavaScript error during click/keyup handler",
                help=out.split(":", 1)[1]
            )
        else:
            raise check50.Failure("JavaScript execution error", help=out)
