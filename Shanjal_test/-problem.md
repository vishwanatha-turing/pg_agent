```markdown
# Problem: Treasure Hunt

## Problem Description

In the mystical land of Algoria, there is a hidden treasure buried somewhere along a straight path of length `N`. The treasure is buried at some position on this path, and your task is to find its exact location. However, there's a twist: you are not allowed to directly check any specific location for the treasure. Instead, you can query the path by asking an oracle about a segment of the path.

The oracle will respond to your query by telling you whether the treasure is within the specified segment or not. The challenge is to determine the exact location of the treasure by minimizing the number of queries to the oracle.

## Input Format

The interaction with the oracle is as follows:

1. You will first be given an integer `N` (2 ≤ N ≤ 10^5), representing the length of the path.
2. You are allowed to make queries to the oracle in the format `? L R`, where `1 ≤ L ≤ R ≤ N`.
3. The oracle will respond with either "YES" if the treasure is within the segment `[L, R]`, or "NO" if it is not.
4. Once you are certain of the treasure's location, output the position `P` (1 ≤ P ≤ N) with the statement `! P`.

## Output Format

- For each query `? L R`, the oracle will respond with "YES" or "NO".
- When you determine the position `P` of the treasure, output `! P`.

## Constraints

- You need to find the position of the treasure with as few queries as possible.
- The position of the treasure is fixed and does not change between queries.

## Example

Consider the following interaction where `N = 10`:

```
Input:
10

Query 1:
? 1 5
Output:
NO

Query 2:
? 6 10
Output:
YES

Query 3:
? 6 8
Output:
NO

Query 4:
? 9 10
Output:
YES

Query 5:
? 9 9
Output:
YES

Final Output:
! 9
```

In this example, the treasure is located at position `9`.

## Notes

- Be mindful of the number of queries you make. Efficiently narrowing down the possible locations of the treasure is crucial.
- You can implement a segment tree or a binary search strategy to minimize the number of queries.
- Remember to flush output after each query to ensure your program interacts correctly with the oracle.
```

This problem involves interactive queries and utilizes segment trees or binary search techniques, making it suitable for a medium-hard difficulty level in competitive programming.