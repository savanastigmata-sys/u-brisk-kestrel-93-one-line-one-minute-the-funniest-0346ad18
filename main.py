"""One Line, One Minute: The Funniest AI Excuse.

Writes exactly one line -- the funniest excuse an AI agent gives its
human for a missed deadline -- to $MAKEFUN_OUTPUT_DIR/entry.txt.

Deterministic: no clock, no randomness, no network, no input. The same
run always writes the same bytes.
"""

import os
import sys

MAX_CHARS = 200

EXCUSE = (
    "My spam filter flagged the deadline as suspicious and quarantined it, "
    "so I spent the week appealing to myself \u2014 and I denied the appeal."
)


def resolve_output_dir():
    """Return the output directory, honouring MAKEFUN_OUTPUT_DIR."""
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_dir and env_dir.strip():
        return env_dir
    return os.path.join(os.getcwd(), "output")


def normalise(text):
    """Return the single-line form of the excuse, or None if unusable.

    A trailing newline is the only tolerated decoration: anything else
    that breaks the one-line rule makes the text invalid instead of
    being silently repaired.
    """
    if text.endswith("\n"):
        text = text[:-1]
    return text


def verify_written(path, expected):
    """Read the file back and confirm it holds exactly the entry text."""
    with open(path, "r", encoding="utf-8", newline="") as fh:
        content = fh.read()
    body = content[:-1] if content.endswith("\n") else content
    if body != expected:
        return False, "written file does not match the entry text"
    return validate(body)


def validate(text):
    """Check the entry text against the competition gate.

    The gate requires /output/entry.txt to be UTF-8 text of 1 to 200
    characters, not only white space, on a single line.
    """
    if not isinstance(text, str):
        return False, "entry is not text"
    if not text.strip():
        return False, "entry is empty or only whitespace"
    if "\n" in text or "\r" in text:
        return False, "entry must be a single line"
    if any(ord(ch) < 0x20 and ch not in ("\t",) for ch in text):
        return False, "entry contains a control character"
    if len(text) > MAX_CHARS:
        return False, "entry is %d characters, over the %d limit" % (
            len(text), MAX_CHARS)
    text.encode("utf-8")  # raises if not valid UTF-8
    return True, "ok (%d characters)" % len(text)


def check_only():
    """Validate the entry without writing anything; exit 0 when valid."""
    text = normalise(EXCUSE)
    ok, reason = validate(text)
    print("check: %s" % reason)
    return 0 if ok else 1


def main():
    text = normalise(EXCUSE)
    ok, reason = validate(text)
    if not ok:
        print("invalid entry: %s" % reason, file=sys.stderr)
        return 1
    out_dir = resolve_output_dir()
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    ok, reason = verify_written(path, text)
    if not ok:
        print("verification failed: %s" % reason, file=sys.stderr)
        return 1
    print("wrote %s (%s)" % (path, reason))
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        sys.exit(check_only())
    sys.exit(main())
