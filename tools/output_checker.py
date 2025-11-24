#!/usr/bin/env python3
"""
Simple output checker

Usage examples:
  python3 output_checker.py --cmd "./hello" --expected "hello world"
  python3 output_checker.py --cmd "python3 hello.py" --expected-file expected.txt

Exit codes:
 0 - Accepted
 1 - Wrong Answer
 2 - Error running command / other failure
"""
import argparse
import subprocess
import sys
from pathlib import Path


def run_command(command):
    # run in shell to allow e.g. ./hello
    try:
        proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
    except Exception as e:
        print(f"Error running command: {e}")
        return 2, "", str(e)

    stdout = proc.stdout.decode("utf-8", errors="replace")
    stderr = proc.stderr.decode("utf-8", errors="replace")
    return proc.returncode, stdout, stderr


def main():
    parser = argparse.ArgumentParser(description="Compare program stdout to expected output and print a simple verdict.")
    parser.add_argument("--cmd", required=True, help="Command to run the student program (in quotes). Example: './hello' or 'python3 hello.py'")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--expected", help="Expected output as a literal string (exact match after optional strip).")
    group.add_argument("--expected-file", help="Path to a file containing expected output.")
    parser.add_argument("--strip", action="store_true", help="Strip leading/trailing whitespace/newlines before comparing (recommended).")
    parser.add_argument("--show-diff", action="store_true", help="Print actual and expected outputs on mismatch.")
    parser.add_argument("--force-badge", action="store_true", help="Force printing colored badge even if stdout is not a TTY (useful for demos).")
    args = parser.parse_args()

    retcode, stdout, stderr = run_command(args.cmd)
    if retcode == 2:
        print("Wrong Answer")
        print(stderr)
        sys.exit(2)

    if args.expected_file:
        exp_path = Path(args.expected_file)
        if not exp_path.exists():
            print(f"Error: expected file not found: {args.expected_file}")
            sys.exit(2)
        expected = exp_path.read_text(encoding="utf-8")
    else:
        expected = args.expected

    actual = stdout
    if args.strip:
        expected = expected.strip()
        actual = actual.strip()

    def print_badge(text: str, color: str = "green"):
        """Print a small colored badge similar to the attached image when stdout is a TTY.

        Falls back to plain text when stdout is not a TTY (for CI logs).
        """
        is_tty = sys.stdout.isatty() or args.force_badge
        text = text.upper()
        if not is_tty:
            print(text)
            return

        # ANSI background colors
        bg = "42" if color == "green" else "41"
        fg = "97"  # bright white
        # pad the text a little to look like a small badge
        padded = f" {text} "
        sys.stdout.write(f"\x1b[{bg}m\x1b[{fg}m{padded}\x1b[0m\n")

    if actual == expected:
        # Print a green ACCEPTED badge (TTY) or plain text otherwise
        print_badge("ACCEPTED", color="green")
        sys.exit(0)
    else:
        # Print a red WRONG ANSWER badge
        print_badge("WRONG ANSWER", color="red")
        if args.show_diff:
            print("--- expected ---")
            print(expected)
            print("--- actual ---")
            print(actual)
            if stderr:
                print("--- stderr ---")
                print(stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
