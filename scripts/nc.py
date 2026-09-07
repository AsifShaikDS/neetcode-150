#!/usr/bin/env python3
"""Small CLI for working through the Neetcode 150 one problem at a time.

    python scripts/nc.py next      what to solve today
    python scripts/nc.py new       scaffold the next problem (or --num 217)
    python scripts/nc.py review    problems due for a repeat under the 4-day rule
    python scripts/nc.py status    progress and current streak
    python scripts/nc.py done      commit and push the finished problem
"""

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOLUTIONS = ROOT / "solutions"
CURRICULUM = ROOT / "curriculum.json"
TEMPLATE = ROOT / "TEMPLATE.md"
TODO = "TODO"
REDO_AFTER_DAYS = 4


# --------------------------------------------------------------------------- data

def load_problems():
    """Flatten curriculum.json into an ordered list of problem dicts."""
    data = json.loads(CURRICULUM.read_text(encoding="utf-8"))
    out = []
    for block in data["blocks"]:
        for group in block["groups"]:
            for num, title, slug, difficulty in group["problems"]:
                out.append({
                    "num": num,
                    "title": title,
                    "slug": slug,
                    "difficulty": difficulty,
                    "topic": group["topic"],
                    "block": block["name"],
                    "weeks": block["weeks"],
                    "dir": SOLUTIONS / f"{num:04d}-{slug}",
                })
    return out


def state(p):
    """not-started | in-progress | done"""
    if not p["dir"].exists():
        return "not-started"
    solution = p["dir"] / "solution.py"
    if not solution.exists() or TODO in solution.read_text(encoding="utf-8"):
        return "in-progress"
    return "done"


def find(problems, num):
    for p in problems:
        if p["num"] == num:
            return p
    sys.exit(f"No problem {num} in curriculum.json")


def next_unstarted(problems):
    for p in problems:
        if state(p) == "not-started":
            return p
    return None


def in_progress(problems):
    return [p for p in problems if state(p) == "in-progress"]


# --------------------------------------------------------------------------- git

def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(r.stderr.strip() or f"git {' '.join(args)} failed")
    return r.stdout.strip()


def commit_dates():
    """Set of dates (local) that have at least one commit."""
    raw = git("log", "--pretty=%ad", "--date=short", check=False)
    return {d for d in raw.splitlines() if d}


def streak():
    days = commit_dates()
    if not days:
        return 0, 0
    today = dt.date.today()
    # current streak may legitimately start yesterday if today isn't done yet
    start = today if today.isoformat() in days else today - dt.timedelta(days=1)
    current = 0
    d = start
    while d.isoformat() in days:
        current += 1
        d -= dt.timedelta(days=1)
    # longest
    sorted_days = sorted(dt.date.fromisoformat(x) for x in days)
    longest = run = 1
    for a, b in zip(sorted_days, sorted_days[1:]):
        run = run + 1 if (b - a).days == 1 else 1
        longest = max(longest, run)
    return current, longest


# --------------------------------------------------------------------------- commands

def cmd_next(_args):
    problems = load_problems()
    pending = in_progress(problems)
    if pending:
        p = pending[0]
        print(f"Still open: {p['num']}. {p['title']}  ({p['difficulty']}, {p['topic']})")
        print(f"           {p['dir'].relative_to(ROOT)}")
        return
    p = next_unstarted(problems)
    if not p:
        print("All 150 done.")
        return
    done = sum(1 for x in problems if state(x) == "done")
    print(f"Next up ({done}/150 done) — block: {p['block']}, weeks {p['weeks']}")
    print(f"  {p['num']}. {p['title']}  [{p['difficulty']}]  {p['topic']}")
    print(f"  https://leetcode.com/problems/{p['slug']}/")
    print("\n  python scripts/nc.py new")


def cmd_new(args):
    problems = load_problems()
    p = find(problems, args.num) if args.num else next_unstarted(problems)
    if not p:
        print("All 150 done.")
        return
    if p["dir"].exists():
        print(f"Already scaffolded: {p['dir'].relative_to(ROOT)}")
        return

    p["dir"].mkdir(parents=True)
    body = TEMPLATE.read_text(encoding="utf-8")
    for key, value in {
        "{{NUM}}": str(p["num"]),
        "{{TITLE}}": p["title"],
        "{{SLUG}}": p["slug"],
        "{{DIFFICULTY}}": p["difficulty"],
        "{{TOPIC}}": p["topic"],
        "{{DATE}}": dt.date.today().isoformat(),
    }.items():
        body = body.replace(key, value)
    (p["dir"] / "README.md").write_text(body, encoding="utf-8")

    (p["dir"] / "solution.py").write_text(
        f'"""{p["num"]}. {p["title"]} — {p["difficulty"]}\n'
        f'https://leetcode.com/problems/{p["slug"]}/\n"""\n\n\n'
        f"class Solution:\n"
        f"    def solve(self):\n"
        f"        {TODO}\n",
        encoding="utf-8",
    )
    print(f"Scaffolded {p['dir'].relative_to(ROOT)}")
    print(f"  https://leetcode.com/problems/{p['slug']}/")
    print("\nWrite the solution, fill in the README, then: python scripts/nc.py done")


def cmd_review(_args):
    """Problems whose write-up says they need a repeat, and are old enough."""
    today = dt.date.today()
    due = []
    for readme in sorted(SOLUTIONS.glob("*/README.md")):
        text = readme.read_text(encoding="utf-8")
        if not re.search(r"^\*\*Repeat:\*\*\s*yes", text, re.M | re.I):
            continue
        m = re.search(r"^\*\*Solved:\*\*\s*(\d{4}-\d{2}-\d{2})", text, re.M)
        if not m:
            continue
        solved = dt.date.fromisoformat(m.group(1))
        age = (today - solved).days
        if age >= REDO_AFTER_DAYS:
            due.append((age, readme.parent.name))
    if not due:
        print("Nothing due for a repeat.")
        return
    print(f"Due for a repeat (marked 'Repeat: yes', {REDO_AFTER_DAYS}+ days old):\n")
    for age, name in sorted(due, reverse=True):
        print(f"  {age:3d}d   {name}")
    print("\nRedo from scratch. Do not open your own solution first.")


def cmd_status(_args):
    problems = load_problems()
    done = [p for p in problems if state(p) == "done"]
    open_now = in_progress(problems)
    current, longest = streak()

    print(f"Solved      {len(done)}/150   ({len(done) * 100 // 150}%)")
    print(f"Streak      {current} day{'s' if current != 1 else ''}   (longest {longest})")
    if open_now:
        print(f"Open        {', '.join(p['dir'].name for p in open_now)}")

    print()
    by_topic = {}
    for p in problems:
        t = by_topic.setdefault(p["topic"], [0, 0])
        t[1] += 1
        if state(p) == "done":
            t[0] += 1
    width = max(len(t) for t in by_topic)
    for topic, (d, total) in by_topic.items():
        bar = "#" * d + "." * (total - d)
        print(f"  {topic:<{width}}  {d:>2}/{total:<2}  {bar}")


def cmd_done(_args):
    problems = load_problems()
    pending = in_progress(problems)
    if pending:
        names = ", ".join(p["dir"].name for p in pending)
        sys.exit(f"Still has a {TODO} in solution.py: {names}\nFinish it before committing.")

    changed = git("status", "--porcelain")
    if not changed:
        print("Nothing to commit.")
        return

    touched = {
        line[3:].split("/")[1]
        for line in changed.splitlines()
        if line[3:].startswith("solutions/") and "/" in line[3:][10:]
    }
    if not touched:
        sys.exit("No changes under solutions/. Commit that by hand if it's something else.")

    subject_parts = []
    for name in sorted(touched):
        p = next((x for x in problems if x["dir"].name == name), None)
        subject_parts.append(f"{p['num']}. {p['title']}" if p else name)
    subject = "Solve " + "; ".join(subject_parts)

    body_lines = []
    for name in sorted(touched):
        readme = SOLUTIONS / name / "README.md"
        if not readme.exists():
            continue
        text = readme.read_text(encoding="utf-8")
        m = re.search(r"^##\s*Approach\s*$(.+?)^##", text, re.M | re.S)
        if m:
            para = " ".join(m.group(1).split())
            if para:
                body_lines.append(para[:400])

    message = subject if not body_lines else subject + "\n\n" + "\n\n".join(body_lines)

    git("add", "-A")
    subprocess.run(["git", "commit", "-F", "-"], cwd=ROOT, input=message,
                   text=True, check=True)
    print(git("log", "--oneline", "-1"))
    print("\nPush with:  git push")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("next", help="what to solve today")
    n = sub.add_parser("new", help="scaffold a problem folder")
    n.add_argument("--num", type=int, help="LeetCode number (default: next in order)")
    sub.add_parser("review", help="problems due for a repeat")
    sub.add_parser("status", help="progress and streak")
    sub.add_parser("done", help="commit the finished problem")

    args = ap.parse_args()
    {"next": cmd_next, "new": cmd_new, "review": cmd_review,
     "status": cmd_status, "done": cmd_done}[args.cmd](args)


if __name__ == "__main__":
    main()
