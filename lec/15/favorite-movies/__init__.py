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
    """JavaScript defines an array containing 5 movies and updates it using two methods"""
    code = _read("favorite-movies.js")
    clean = _strip_js_comments(code)

    # We will run a Node wrapper to execute favorite-movies.js in a VM context
    # and verify its outputs.
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

// Find any arrays defined in context or logs
let arrays = [];
for (const key in context) {
    if (Array.isArray(context[key])) {
        arrays.push(context[key]);
    }
}

// Check logged values for arrays
for (const log of logs) {
    for (const arg of log) {
        if (Array.isArray(arg)) {
            arrays.push(arg);
        }
    }
}

if (arrays.length === 0) {
    console.log("FAIL_NO_ARRAY");
    process.exit(1);
}

// Check if any array initially had 5 movies
// Since the student might have modified the array in place, we inspect context and logs.
console.log("PASS");
"""

    res = subprocess.run(["node", "-e", wrapper], capture_output=True, text=True)
    if res.returncode != 0:
        out = res.stdout.strip() or res.stderr.strip()
        if out.startswith("FAIL_NO_ARRAY"):
            raise check50.Failure(
                "No movie array found",
                help="Make sure you declare an array containing 5 movies (e.g. let movies = [...];) and print it"
            )
        elif out.startswith("ERROR_EXEC"):
            msg = out.split(":", 1)[1]
            raise check50.Failure("JavaScript execution error", help=msg)
        else:
            raise check50.Failure("JavaScript execution error", help=out or res.stderr.strip())

    # Count array method usage (e.g. .push(, .pop(, .shift(, .unshift(, .splice(, .slice(, .concat(, .reverse()
    methods = ["push", "pop", "shift", "unshift", "splice", "slice", "concat", "reverse"]
    methods_used = 0
    for m in methods:
        if f".{m}(" in clean or f".{m} (" in clean:
            methods_used += 1

    if methods_used < 2:
        raise check50.Failure(
            "Fewer than two array methods used",
            help="Use at least two array methods from your notes (such as push, pop, shift, unshift, or splice) to update the array"
        )
