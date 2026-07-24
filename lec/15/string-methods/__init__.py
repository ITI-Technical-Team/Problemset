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
    """string-methods.js exists"""
    check50.exists("string-methods.js")


@check50.check(exists)
def checks_string_methods():
    """JavaScript defines a quote string and updates it using two methods"""
    code = _read("string-methods.js")
    clean = _strip_js_comments(code)

    # We will run a Node wrapper to execute string-methods.js in a VM context
    # and verify its outputs.
    wrapper = r"""
const fs = require('fs');
const vm = require('vm');
const code = fs.readFileSync('string-methods.js', 'utf8');

let logs = [];
const context = {
    console: {
        log: (...args) => {
            logs.push(args.join(' '));
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

if (logs.length < 2) {
    console.log("FAIL_NO_LOGS");
    process.exit(1);
}
console.log("PASS");
"""

    res = subprocess.run(["node", "-e", wrapper], capture_output=True, text=True)
    if res.returncode != 0:
        out = res.stdout.strip() or res.stderr.strip()
        if out.startswith("FAIL_NO_LOGS"):
            raise check50.Failure(
                "Missing console output",
                help="Make sure you print the original quote and the results of your string methods to the console"
            )
        elif out.startswith("ERROR_EXEC"):
            msg = out.split(":", 1)[1]
            raise check50.Failure("JavaScript execution error", help=msg)
        else:
            raise check50.Failure("JavaScript execution error", help=out or res.stderr.strip())

    # Count string method usage (e.g. toUpperCase, toLowerCase, replace, split, indexOf, slice, charAt, trim, includes, concat, substring, substr)
    methods = [
        "toUpperCase", "toLowerCase", "replace", "split", "indexOf",
        "slice", "charAt", "trim", "includes", "concat", "substring", "substr"
    ]
    methods_used = 0
    for m in methods:
        if f".{m}(" in clean or f".{m} (" in clean:
            methods_used += 1

    if methods_used < 2:
        raise check50.Failure(
            "Fewer than two string methods used",
            help="Use at least two string methods from your notes (such as toUpperCase, toLowerCase, replace, split, indexOf, slice, or trim)"
        )
