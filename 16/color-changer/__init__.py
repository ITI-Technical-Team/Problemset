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
def has_quote_elements():
    """index.html has elements with id='quote' and id='author'"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    if not soup.find(id="quote"):
        raise check50.Failure(
            "Missing element with id='quote'",
            help="Add an HTML element like `<p id=\"quote\"></p>` to display the quote text"
        )
    if not soup.find(id="author"):
         raise check50.Failure(
            "Missing element with id='author'",
            help="Add an HTML element like `<p id=\"author\"></p>` to display the author's name"
        )


@check50.check(exists)
def has_button():
    """index.html contains a button to generate new quote"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    btn = soup.find("button")
    if not btn:
         raise check50.Failure("Missing <button> element")
         
    onclick = btn.get("onclick", "")
    # Check if click listener is defined in HTML or script
    if not onclick and "addeventlistener" not in html.lower():
         raise check50.Failure(
            "Button does not trigger RandomQuotes() on click",
            help="Add onclick=\"RandomQuotes()\" to your button or use addEventListener in JavaScript"
        )


# ─── JS checks — functional execution ────────────────────────────────────────

@check50.check(has_quote_elements)
def verifies_quotes_and_logic():
    """JavaScript declares quotes object and RandomQuotes() selects and updates elements correctly"""
    html = _read("index.html")
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script")
    if not script:
        raise check50.Failure("Missing <script> tag")
        
    js_code = script.string or ""
    js_clean = _strip_js_comments(js_code)

    # Active code checks
    if "randomquotes" not in js_clean.lower():
         raise check50.Failure(
            "Missing RandomQuotes() function",
            help="Define the function: function RandomQuotes() { ... }"
        )
    if "math.random" not in js_clean.lower():
        raise check50.Failure("Missing Math.random() call in active JavaScript")
    if "math.floor" not in js_clean.lower():
        raise check50.Failure("Missing Math.floor() call in active JavaScript")

    # Node environment setup to validate quotes data structure and random selection
    mock_env = r"""
let _quoteText = "";
let _authorText = "";
let mockQuoteEl = {
    get innerHTML()    { return _quoteText; },
    set innerHTML(v)   { _quoteText = v; },
    get textContent()  { return _quoteText; },
    set textContent(v) { _quoteText = v; },
    get innerText()    { return _quoteText; },
    set innerText(v)   { _quoteText = v; }
};
let mockAuthorEl = {
    get innerHTML()    { return _authorText; },
    set innerHTML(v)   { _authorText = v; },
    get textContent()  { return _authorText; },
    set textContent(v) { _authorText = v; },
    get innerText()    { return _authorText; },
    set innerText(v)   { _authorText = v; }
};

global.document = {
    getElementById: (id) => {
        if (id === "quote") return mockQuoteEl;
        if (id === "author") return mockAuthorEl;
        return null;
    }
};

let _mockRandomVal = 0.0;
global.Math.random = () => _mockRandomVal;
"""

    test_harness = r"""
// 1. Verify quotes object exists and has 10 items
if (typeof quotes === "undefined") {
    console.log("FAIL_NO_QUOTES");
    process.exit(1);
}
if (typeof quotes !== "object" || quotes === null) {
    console.log("FAIL_QUOTES_TYPE");
    process.exit(1);
}
let count = 0;
for (let i = 0; i < 10; i++) {
    if (quotes[i] || quotes[String(i)]) count++;
}
if (count < 10) {
    console.log("FAIL_QUOTES_COUNT:" + count);
    process.exit(1);
}

// Check for required Oscar Wilde quote
let has_oscar = false;
for (const key in quotes) {
    const entry = quotes[key];
    if (entry.author && entry.author.toLowerCase().includes("oscar wilde")) {
        has_oscar = true;
        break;
    }
}
if (!has_oscar) {
    console.log("FAIL_NO_OSCAR");
    process.exit(1);
}

// 2. Verify RandomQuotes function exists
if (typeof RandomQuotes !== "function") {
    console.log("FAIL_NO_FUNCTION");
    process.exit(1);
}

// 3. Test selection logic for different mock random values
const test_cases = [
    { rand: 0.0,  idx: 0 },
    { rand: 0.35, idx: 3 },
    { rand: 0.99, idx: 9 }
];

for (const tc of test_cases) {
    _quoteText = "";
    _authorText = "";
    _mockRandomVal = tc.rand;
    
    try {
        RandomQuotes();
    } catch (e) {
        console.log("ERROR:" + e.message);
        process.exit(1);
    }
    
    const expected = quotes[tc.idx];
    if (!_quoteText || !_quoteText.toLowerCase().includes(expected.quote.toLowerCase())) {
        console.log(`FAIL_RANDOM_SELECTION:${tc.idx}:${_quoteText}:${expected.quote}`);
        process.exit(1);
    }
    if (!_authorText || !_authorText.toLowerCase().includes(expected.author.toLowerCase())) {
        console.log(`FAIL_AUTHOR_SELECTION:${tc.idx}:${_authorText}:${expected.author}`);
        process.exit(1);
    }
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
                help="Declare a quotes object containing 10 different quotes: let quotes = { 0: { quote: '...', author: '...' }, ... };"
            )
        elif out.startswith("FAIL_QUOTES_TYPE"):
            raise check50.Failure(
                "Variable 'quotes' should be an object",
                help="Make sure quotes is declared as an object: let quotes = { ... }"
            )
        elif out.startswith("FAIL_QUOTES_COUNT"):
            got = out.split(":", 1)[1]
            raise check50.Failure(
                f"Quotes object contains {got} items, expected exactly 10",
                help="Define exactly 10 quotes with keys from 0 to 9"
            )
        elif out.startswith("FAIL_NO_OSCAR"):
            raise check50.Failure(
                "Quotes object is missing the required quotes",
                help="Make sure to include the 10 quotes provided in the task description, including the Oscar Wilde quote"
            )
        elif out.startswith("FAIL_NO_FUNCTION"):
            raise check50.Failure(
                "Missing RandomQuotes() function",
                help="Define the function: function RandomQuotes() { ... }"
            )
        elif out.startswith("FAIL_RANDOM_SELECTION"):
            parts = out.split(":")
            idx, got, expected = parts[1], parts[2], parts[3]
            raise check50.Failure(
                f"RandomQuotes() did not load the correct quote for random index {idx}",
                help=f"Expected quote: {expected!r}. Got: {got!r}"
            )
        elif out.startswith("FAIL_AUTHOR_SELECTION"):
            parts = out.split(":")
            idx, got, expected = parts[1], parts[2], parts[3]
            raise check50.Failure(
                f"RandomQuotes() did not load the correct author for random index {idx}",
                help=f"Expected author: {expected!r}. Got: {got!r}"
            )
        elif out.startswith("ERROR"):
            raise check50.Failure(
                "JavaScript error inside RandomQuotes()",
                help=out.split(":", 1)[1]
            )
        else:
            raise check50.Failure("JavaScript execution error", help=out)
