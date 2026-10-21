# 217. Contains Duplicate

**Difficulty:** Easy · **Topic:** Arrays & Hashing · [Problem](https://leetcode.com/problems/contains-duplicate/)

**Solved:** 2026-09-08
**Time to first working solution:** 25 min
**Repeat:** yes

---

## The problem in one sentence

Given a list of integers, say whether any value shows up more than once.

## Approach

Walk the list once and keep a set of everything already seen. If the current value is
already in that set, a duplicate exists and you can return immediately. Reaching the end
without a hit means every value was distinct.

The observation worth stating is that you never need to know *which* value repeats, or how
often, or where. The question is a yes/no, so the moment you see a repeat you are done. That
is what lets this return early instead of counting everything first.

Sorting and then comparing neighbours also works and uses no extra space, but it costs
O(n log n) and destroys the input order. The set trades space for time, which is the right
trade when n is large and the answer is usually found early.

## Complexity

- Time: O(n)
- Space: O(n)

Each element is looked up and inserted at most once, and both are O(1) average on a hash
set, so the whole pass is linear. The set holds at most n elements, which is the space. Worst
case for time is an all-distinct input, where the early return never fires.

## What I got wrong first

_To fill in on the repeat. Leave it honest, including "nothing, this one was straightforward"._

## The pattern

Set as a seen-tracker, which is the base case for most of Arrays & Hashing. The same move
drives Two Sum (store the complement you need), Longest Consecutive Sequence (O(1) membership
to walk a run), and Happy Number (detect a cycle by remembering what you already visited).
Whenever a problem asks "has this appeared before", reach for the set before anything else.
