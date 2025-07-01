from collections import Counter

def findPairs(nums, k):
    if k < 0:
        return 0  # Absolute difference can't be negative

    count = 0
    freq = Counter(nums)

    if k == 0:
        # Count numbers that appear more than once
        count = sum(1 for val in freq.values() if val > 1)
    else:
        # Count unique pairs (num, num + k)
        for num in freq:
            if num + k in freq:
                count += 1

    return count