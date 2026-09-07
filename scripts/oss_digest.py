#!/usr/bin/env python3
"""Morning shortlist of open-source issues worth a look.

This does not open pull requests and it does not write code. It reads the issue
queues of the repositories that were verified as actually merging outside
contributions, filters out the ones that are already spoken for, and prints what
is left so the daily habit starts from a real candidate instead of a search box.

    python scripts/oss_digest.py
    python scripts/oss_digest.py --days 60 --limit 5

Requires the GitHub CLI to be authenticated (`gh auth status`).
"""

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import time

# Verified 2026-09-05: merge rate, distinct outside authors, and time-to-merge all
# checked. Repos that close far more than they merge are deliberately absent.
REPOS = [
    ("docling-project/docling", "your domain, and the library the flagship runs on"),
    ("dottxt-ai/outlines", "a custom type is the fastest realistic first merge"),
    ("confident-ai/deepeval", "actively invites new metrics"),
    ("neuml/txtai", "merges fast, but the queue is usually empty"),
    ("UKGovernmentBEIS/inspect_ai", "highest prestige, gated on a maintainer label"),
]

# An issue carrying one of these is already someone else's.
TAKEN = {"in progress", "in-progress", "claimed", "assigned", "wip",
         "needs triage", "duplicate", "wontfix", "stale"}

GH_CANDIDATES = [
    "gh",
    r"C:\Program Files\GitHub CLI\gh.exe",
    "/c/Program Files/GitHub CLI/gh.exe",
]


def gh_bin():
    for c in GH_CANDIDATES:
        if os.path.sep in c or "/" in c:
            if os.path.exists(c):
                return c
        elif shutil.which(c):
            return shutil.which(c)
    sys.exit("GitHub CLI not found. Install it, or add gh to PATH.")


def search(gh, query):
    """Run one search, retrying once if GitHub's secondary rate limit trips."""
    for attempt in range(2):
        r = subprocess.run(
            [gh, "api", "-X", "GET", "search/issues",
             "-f", f"q={query}", "-F", "per_page=100",
             "--jq", ".items[] | {number,title,labels:[.labels[].name],comments,created_at,html_url}"],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            return r.stdout, None
        if "rate limit" in r.stderr.lower() and attempt == 0:
            time.sleep(20)
            continue
        err = (r.stderr.strip().splitlines() or ["request failed"])[-1]
        return None, err.split(" For more on scraping")[0]
    return None, "rate limited"


def fetch_all(gh, days):
    """One search across every repo — the search API rate-limits per request,
    not per result, so five `repo:` qualifiers cost a fifth of five queries."""
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).strftime("%Y-%m-%d")
    repos = " ".join(f"repo:{r}" for r, _ in REPOS)
    query = f"{repos} is:issue is:open no:assignee created:>={since} sort:created-desc"
    stdout, err = search(gh, query)
    if err:
        return None, err

    by_repo = {r: [] for r, _ in REPOS}
    now = dt.datetime.now(dt.timezone.utc)
    for line in stdout.splitlines():
        if not line.strip():
            continue
        it = json.loads(line)
        labels = {l.lower() for l in it["labels"]}
        if labels & TAKEN:
            continue
        if it["comments"] > 3:          # an active thread is usually already owned
            continue
        # html_url looks like https://github.com/<owner>/<repo>/issues/<n>
        repo = "/".join(it["html_url"].split("/")[3:5])
        if repo not in by_repo:
            continue
        created = dt.datetime.fromisoformat(it["created_at"].replace("Z", "+00:00"))
        it["age"] = (now - created).days
        by_repo[repo].append(it)
    return by_repo, None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=30, help="how far back to look (default 30)")
    ap.add_argument("--limit", type=int, default=4, help="issues per repo (default 4)")
    args = ap.parse_args()

    gh = gh_bin()
    total = 0

    print()
    print("  Open source — unassigned, quiet, and recent")
    print()

    by_repo, err = fetch_all(gh, args.days)
    if err:
        sys.exit(f"  ! {err}\n")

    for repo, why in REPOS:
        items = by_repo[repo][: args.limit]
        print(f"  {repo}")
        print(f"    {why}")
        if not items:
            print("    nothing unclaimed in the window")
        else:
            for it in items:
                labels = ", ".join(it["labels"][:3]) or "no labels"
                print(f"    #{it['number']:<6} {it['title'][:66]}")
                print(f"    {'':<7} {it['age']}d · {it['comments']} comments · {labels}")
                print(f"    {'':<7} {it['html_url']}")
                total += 1
        print()

    print(f"  {total} candidate{'s' if total != 1 else ''}.")
    print()
    print("  Reproduce it first. If you cannot reproduce it, that comment is itself")
    print("  a useful contribution and takes two minutes. Do not open a pull request")
    print("  on a repo you have not actually run.")
    print()


if __name__ == "__main__":
    main()
