# Week 3 · Exercise 2, Part 2 — Josep Coll
"""
Read the two run logs and print the bill two ways.

Both agents kept calling tools after they had already finished the job — a
small-model failure, and one that hits both roads. So a single "total" would
say as much about the driver as about the road. This prints:

  * TASK  — the cumulative bill up to and including the call that completed the
            task (the like-for-like comparison of the same work);
  * FULL  — everything the meter saw, flailing included.

    uv run python tally.py
"""
import re
import sys
from pathlib import Path

RUNS = Path(__file__).resolve().parent / "runs"
CALL = re.compile(r"call #(\d+): prompt_tokens=(\d+) completion_tokens=(\d+)")

# The call at which the comment actually landed on the forum, read off the logs:
# road 1 posted with run_command on call 2; road 2's click went through on call 3.
DONE_AT = {"road-1-cli.log": 2, "road-2-browser.log": 3}


def tally(path, done_at):
    calls = [(int(a), int(b), int(c)) for a, b, c in CALL.findall(path.read_text())]
    def total(upto):
        sel = [c for c in calls if c[0] <= upto]
        return len(sel), sum(c[1] for c in sel), sum(c[2] for c in sel)
    return total(done_at), total(10**9)


def main():
    rows = {}
    for name, done in DONE_AT.items():
        f = RUNS / name
        if not f.is_file():
            sys.exit(f"missing {f}")
        rows[name] = tally(f, done)

    for label, idx in (("TASK (up to the call that posted)", 0), ("FULL RUN (what the meter saw)", 1)):
        print(f"\n{label}")
        print(f"{'road':<24}{'calls':>6}{'prompt':>10}{'completion':>12}{'total':>10}")
        totals = []
        for name, res in rows.items():
            n, p, c = res[idx]
            totals.append(p + c)
            print(f"{name:<24}{n:>6}{p:>10}{c:>12}{p + c:>10}")
        print(f"{'ratio browser/CLI':<24}{'':>6}{'':>10}{'':>12}{totals[1] / totals[0]:>9.2f}x")


if __name__ == "__main__":
    main()
