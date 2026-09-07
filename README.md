# Neetcode 150

Working through the Neetcode 150 in Python, one problem at a time, with the reasoning written
down. Interview preparation done in the open.

The write-up matters more to me than the solution. Anyone can look up a working answer to
these; the thing worth keeping is the key observation, the wrong turn I took first, and the
name of the pattern so I recognise it the next time it turns up wearing a different story.

## Layout

```
curriculum.json              the 150, in order, grouped by topic
TEMPLATE.md                  the write-up template
solutions/0001-two-sum/
  README.md                  the write-up
  solution.py                the code
scripts/nc.py                the small CLI below
scripts/morning.ps1          what runs each weekday morning
```

## How I work through it

```bash
python scripts/nc.py next      # what to solve today
python scripts/nc.py new       # scaffold the folder for it
python scripts/nc.py review    # what is due for a repeat
python scripts/nc.py status    # progress and streak
python scripts/nc.py done      # commit it
```

`nc.py done` refuses to commit while `solution.py` still contains a `TODO`, and it builds the
commit message from the Approach section of the write-up. If the approach is not written, the
commit says nothing, which is the point.

## Two rules I am holding myself to

**Twenty-five minutes.** If I have not got it by then, I read the solution, understand it
properly, close it, and reimplement from scratch. Grinding a problem for two hours feels
productive and teaches almost nothing.

**Repeat after four days.** Anything I did not get unaided is marked `Repeat: yes` in its
write-up and comes back around. `nc.py review` lists what is due. Spaced repetition of
patterns is what actually transfers; volume alone does not.

## Progress

Run `python scripts/nc.py status` for the current count. The order follows the standard
Neetcode blocks: foundations (arrays, two pointers, sliding window, stack, binary search,
linked lists), then structures (trees, tries, heaps, backtracking, graphs), then the hard
patterns (dynamic programming, greedy, intervals, math, bit manipulation).
