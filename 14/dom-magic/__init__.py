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
def has_script():
    """index.html contains a <script> block"""
    if "<script" not in _html():
        raise check50.Failure(
            "Missing <script> tag",
            help="Add a `<script>` element containing your JavaScript code inside index.html"
        )


# ─── JS checks ────────────────────────────────────────────────────────────────

@check50.check(has_script)
def has_prompts():
    """JavaScript prompts for name and 3 subject grades"""
    html = _html()
    # Should call prompt at least 4 times (name + 3 subjects)
    prompts = re.findall(r'prompt\s*\(', html)
    if len(prompts) < 4:
        raise check50.Failure(
            f"Found {len(prompts)} prompt(s), expected at least 4",
            help="Prompt the user for: Name, Grade 1, Grade 2, and Grade 3"
        )


@check50.check(has_script)
def converts_grades():
    """JavaScript converts grades to numbers before adding them"""
    html = _html()
    # Check for Number() or parseFloat() or parseInt() or + operator conversion
    if "number(" not in html and "parsefloat(" not in html and "parseint(" not in html and "+" not in html:
        raise check50.Failure(
            "Grades do not appear to be converted to numbers",
            help="Use Number(prompt(...)) or parseFloat(prompt(...)) so math operations work correctly"
        )


@check50.check(has_script)
def calculates_totals():
    """JavaScript calculates the total and average of the 3 grades"""
    html = _html()
    # Must divide total by 3 for average
    if "/ 3" not in html and "/3" not in html:
         raise check50.Failure(
            "Average calculation is missing or incorrect",
            help="Divide the sum of the 3 grades by 3 to calculate the average"
        )


@check50.check(has_script)
def conditional_check():
    """JavaScript decides if the student passed or failed (average >= 50)"""
    html = _html()
    if "50" not in html:
        raise check50.Failure(
            "Missing threshold check for passing grade",
            help="Check if average is greater than or equal to 50"
        )
    if "pass" not in html or "fail" not in html:
        raise check50.Failure(
            "Missing Pass/Fail result outcomes",
            help="Set result to 'Pass' if average >= 50, otherwise 'Fail'"
        )


@check50.check(has_script)
def outputs_result():
    """JavaScript outputs student name, grades, total, average, and result"""
    html = _html()
    if "alert(" not in html and "console.log(" not in html:
         raise check50.Failure(
            "No output method detected",
            help="Use alert() or console.log() to display the final student card details"
        )
    if "tofixed(2)" not in html and "tofixed(2" not in html:
         raise check50.Failure(
            "Average is not formatted to 2 decimal places",
            help="Use average.toFixed(2) to format the average score"
        )


# ─── CSS checks ───────────────────────────────────────────────────────────────

@check50.check(exists)
def checks_css_styling():
    """CSS styles the heading and the body"""
    html = _html()
    
    # Check for center alignment
    if "text-align" not in html or "center" not in html:
         raise check50.Failure(
            "Heading or page content is not centered",
            help="Add 'text-align: center;' to align your heading/content"
        )
         
    # Check for heading color styling
    if "h1" not in html:
        raise check50.Failure("Missing heading <h1> element")
        
    # Check for color in css
    if "color" not in html:
        raise check50.Failure(
            "Page heading is missing a custom color",
            help="Add color: darkred; (or any nice color) to your CSS rules"
        )
