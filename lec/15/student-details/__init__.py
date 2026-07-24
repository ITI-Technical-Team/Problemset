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
    """student-details.js exists"""
    check50.exists("student-details.js")


@check50.check(exists)
def checks_student_object():
    """JavaScript defines the student object and modifies its age"""
    code = _read("student-details.js")
    clean = _strip_js_comments(code)

    # We will run a Node wrapper to execute student-details.js in a VM context
    # and inspect the student object properties.
    wrapper = r"""
const fs = require('fs');
const vm = require('vm');
const code = fs.readFileSync('student-details.js', 'utf8');

let logs = [];
const context = {
    console: {
        log: (...args) => {
            logs.push(args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' '));
        }
    }
};

vm.createContext(context);
try {
    vm.runInContext(code + "\nconsole.log('STUDENT_CHECK', JSON.stringify(student));", context);
} catch (e) {
    if (e.message && e.message.includes('student is not defined')) {
        console.log("FAIL_STUDENT_MISSING");
    } else {
        console.log("ERROR_EXEC:" + e.message);
    }
    process.exit(1);
}

const checkLog = logs.find(l => l.startsWith('STUDENT_CHECK'));
if (!checkLog) {
    console.log("FAIL_STUDENT_MISSING");
    process.exit(1);
}

const studentJSON = checkLog.substring('STUDENT_CHECK '.length);
let student;
try {
    student = JSON.parse(studentJSON);
} catch (e) {
    console.log("FAIL_STUDENT_MISSING");
    process.exit(1);
}

// Check properties (case-insensitive keys check)
const keys = Object.keys(student).map(k => k.toLowerCase());
if (!keys.includes("name") || !keys.includes("age") || !keys.includes("department")) {
    console.log("FAIL_PROPERTIES_MISSING");
    process.exit(1);
}

// Find key names
const nameKey = Object.keys(student).find(k => k.toLowerCase() === "name");
const ageKey = Object.keys(student).find(k => k.toLowerCase() === "age");
const deptKey = Object.keys(student).find(k => k.toLowerCase() === "department");

if (typeof student[nameKey] !== 'string' || typeof student[deptKey] !== 'string' || typeof student[ageKey] !== 'number') {
    console.log("FAIL_TYPES");
    process.exit(1);
}

// Verify that logs are present (excluding the STUDENT_CHECK log)
const studentLogs = logs.filter(l => !l.startsWith('STUDENT_CHECK'));
if (studentLogs.length < 2) {
    console.log("FAIL_LOGS_COUNT");
    process.exit(1);
}

console.log("PASS");
"""

    res = subprocess.run(["node", "-e", wrapper], capture_output=True, text=True)
    if res.returncode != 0:
        out = res.stdout.strip() or res.stderr.strip()
        if out.startswith("FAIL_STUDENT_MISSING"):
            raise check50.Failure(
                "Variable 'student' is not defined",
                help="Make sure you declare a student object using: let student = { ... };"
            )
        elif out.startswith("FAIL_PROPERTIES_MISSING"):
            raise check50.Failure(
                "Missing student properties",
                help="Ensure your student object has properties: name, age, and department"
            )
        elif out.startswith("FAIL_TYPES"):
            raise check50.Failure(
                "Incorrect property types",
                help="Ensure 'name' and 'department' are strings, and 'age' is a number"
            )
        elif out.startswith("FAIL_LOGS_COUNT"):
            raise check50.Failure(
                "Missing console output",
                help="Make sure you print the student object information to the console"
            )
        elif out.startswith("ERROR_EXEC"):
            msg = out.split(":", 1)[1]
            raise check50.Failure("JavaScript execution error", help=msg)
        else:
            raise check50.Failure("JavaScript execution error", help=out or res.stderr.strip())

    # We also check that the student's age was modified in the code file.
    # Checks for student.age = ... or student['age'] = ...
    if not re.search(r'student(?:\.age|\[\s*[\'"]age[\'"]\s*\])\s*=', clean):
        raise check50.Failure(
            "Student age was not modified",
            help="Update the student's age property (e.g. student.age = 21;)"
        )
