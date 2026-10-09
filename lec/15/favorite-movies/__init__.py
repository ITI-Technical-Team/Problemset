import check50
import re
import subprocess


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
    """favorite-movies.js exists"""
    check50.exists("favorite-movies.js")


@check50.check(exists)
def checks_movies_array():
    """JavaScript defines an array containing 5 movies, logs original & updated arrays, and uses two methods"""
    code = _read("favorite-movies.js")
    clean = _strip_js_comments(code)

    wrapper = r"""
const fs = require('fs');
const vm = require('vm');
const code = fs.readFileSync('favorite-movies.js', 'utf8');

let logs = [];
const context = {
    console: {
        log: (...args) => {
            logs.push(args);
        }
    }
};

vm.createContext(context);
try {
    vm.runInContext(code, context);
} catch (e) {
    console.log("ERROR_EXEC:" + e.message);
    process.exit(1);
}

// Find any movie arrays declared in context or logged
let foundArray = null;
for (const key in context) {
    if (Array.isArray(context[key])) {
        foundArray = context[key];
        break;
    }
}

// Check logged arrays
let arrayLogs = [];
for (const log of logs) {
    for (const arg of log) {
        if (Array.isArray(arg)) {
            arrayLogs.push(arg);
            if (!foundArray) foundArray = arg;
        } else if (typeof arg === 'string' && (arg.includes('[') || arg.includes(','))) {
            arrayLogs.push(arg);
        }
    }
}

if (!foundArray && arrayLogs.length === 0) {
    console.log("FAIL_NO_ARRAY");
    process.exit(1);
}

// Inspect initial array in source code before methods
const arrayMatch = code.match(/\[([\s\S]*?)\]/);
if (!arrayMatch) {
    console.log("FAIL_NO_ARRAY");
    process.exit(1);
}

const rawElements = arrayMatch[1].split(',').map(s => s.replace(/['"\s\n\r]/g, '').trim()).filter(Boolean);
if (rawElements.length < 5) {
    console.log("FAIL_INITIAL_COUNT");
    process.exit(1);
}

// Check that console.log printed the array (or logged array values) at least twice
if (arrayLogs.length < 2) {
    console.log("FAIL_LOGS_COUNT");
    process.exit(1);
}

console.log("PASS");
"""

    res = subprocess.run(["node", "-e", wrapper], capture_output=True, text=True)
    if res.returncode != 0:
        out = res.stdout.strip() or res.stderr.strip()
        if out.startswith("FAIL_NO_ARRAY"):
            raise check50.Failure(
                "No movie array found",
                help="Declare an array containing 5 movie titles (e.g. let movies = ['Inception', 'The Dark Knight', 'Interstellar', 'The Matrix', 'Avatar'];)"
            )
        elif out.startswith("FAIL_INITIAL_COUNT"):
            raise check50.Failure(
                "Initial movie array contains fewer than 5 movies",
                help="Initialize your movie array with at least 5 movie title strings."
            )
        elif out.startswith("FAIL_LOGS_COUNT"):
            raise check50.Failure(
                "Missing console log output of movie array",
                help="Make sure to log the movie array using console.log(movies) both before and after updating it."
            )
        elif out.startswith("ERROR_EXEC"):
            msg = out.split(":", 1)[1]
            raise check50.Failure("JavaScript execution error", help=msg)
        else:
            raise check50.Failure("JavaScript execution error", help=out or res.stderr.strip())

    # Count array method usage
    methods = ["push", "pop", "shift", "unshift", "splice", "slice", "concat", "reverse"]
    methods_used = 0
    for m in methods:
        if f".{m}(" in clean or f".{m} (" in clean:
            # For push/unshift, check that it's not empty string ""
            if m in ["push", "unshift"]:
                if re.search(r'\.' + m + r'\(\s*[\'"]\s*[\'"]\s*\)', clean):
                    raise check50.Failure(
                        f"Array method .{m}() was called with an empty string",
                        help=f"Pass a valid movie title string when calling .{m}() (e.g. movies.push('The Godfather');)"
                    )
            methods_used += 1

    if methods_used < 2:
        raise check50.Failure(
            "Fewer than two array methods used",
            help="Use at least two array methods from your notes (such as push, pop, shift, unshift, or splice) to update the array"
        )
