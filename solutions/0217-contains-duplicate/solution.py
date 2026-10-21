"""217. Contains Duplicate — Easy
https://leetcode.com/problems/contains-duplicate/
"""

from typing import List


class Solution:
    def containsDuplicate(self, nums: List[int]) -> bool:
        contains = set()
        for n in nums:
            if n in contains:
                return True
            else:
                contains.add(n)

        return False
