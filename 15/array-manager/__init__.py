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
def declares_fruits_array():
    """JavaScript declares the initial fruits array"""
    html = _html()
    if "fruits" not in html:
        raise check50.Failure(
            "Missing 'fruits' variable",
            help="Declare an array named 'fruits': let fruits = ['apple', 'banana', 'cherry'];"
        )


@check50.check(has_script)
def prompts_and_lowercases():
    """JavaScript prompts the user and converts the fruit name to lowercase"""
    html = _html()
    if "prompt(" not in html:
        raise check50.Failure("Missing prompt() call")
    if "tolowercase()" not in html:
        raise check50.Failure(
            "Missing .toLowerCase() call",
            help="Convert the input to lowercase: input.toLowerCase()"
        )


@check50.check(has_script)
def checks_existence_and_adds():
    """JavaScript checks existence with includes() and adds fruit using push()"""
    html = _html()
    if "includes(" not in html:
        raise check50.Failure(
            "Missing .includes() check",
            help="Use fruits.includes(fruitName) to check if it's already in the array"
        )
    if "push(" not in html:
        raise check50.Failure(
            "Missing .push() call",
            help="Use fruits.push(fruitName) to add the fruit to the end of the array"
        )


@check50.check(has_script)
def mutates_array():
    """JavaScript uses splice() and unshift() to update the fruits list"""
    html = _html()
    if "splice(" not in html:
        raise check50.Failure(
            "Missing .splice() call",
            help="Use fruits.splice(1, 1, 'blueberry') to replace the second fruit"
        )
    if "unshift(" not in html:
        raise check50.Failure(
            "Missing .unshift() call",
            help="Use fruits.unshift('grape') to add 'grape' to the beginning"
        )


@check50.check(has_script)
def sorts_and_reverses():
    """JavaScript sorts and reverses the array"""
    html = _html()
    if "sort()" not in html:
        raise check50.Failure(
            "Missing .sort() call",
            help="Use fruits.sort() to sort alphabetically"
        )
    if "reverse()" not in html:
         raise check50.Failure(
            "Missing .reverse() call",
            help="Use fruits.reverse() to reverse the alphabetical order"
        )


@check50.check(has_script)
def outputs_joined_string():
    """JavaScript joins the array and displays it in an alert"""
    html = _html()
    if "join(" not in html:
        raise check50.Failure(
            "Missing .join() call",
            help="Use fruits.join(', ') to join the array elements"
        )
    if "alert(" not in html:
        raise check50.Failure(
            "Missing alert() output",
            help="Display the final fruits string in an alert popup"
        )


@check50.check(has_script)
def logs_with_foreach_and_uppercase():
    """JavaScript uses arrow function inside forEach() and logs uppercase fruit names"""
    html = _read("index.html")
    if "forEach" not in html:
        raise check50.Failure(
            "Missing .forEach() loop",
            help="Use fruits.forEach(...) to loop through the final list"
        )
    if "=>" not in html:
        raise check50.Failure(
            "forEach must use an arrow function",
            help="Use an arrow function: fruits.forEach((fruit, index) => { ... })"
        )
    if "touppercase" not in html.lower():
        raise check50.Failure(
            "Missing .toUpperCase() call in the log output",
            help="Convert the fruit name to uppercase inside the console log: fruit.toUpperCase()"
        )
