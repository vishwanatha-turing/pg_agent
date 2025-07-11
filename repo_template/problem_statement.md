# Array Splitting for Maximum Product

In a kingdom where resources are limited, the king needs to distribute an array of treasures (represented as integers) among his subjects in such a way that the product of the sums of treasures allocated to two groups is maximized. The king has devised a plan to create two groups from the array: one group will contain the first `k` treasures, and the other will contain the remaining `n - k` treasures, where `n` is the total number of treasures in the array. Your task is to help the king determine the maximum possible product of the sums of these two groups by choosing the appropriate `k`.

Given the treasures, you need to compute the maximum product of the sums that can be achieved by splitting the array into two non-empty groups.

## Input Format
- The first line of input contains an integer `n` (2 ≤ n ≤ 1000), which represents the number of treasures.
- The second line contains `n` integers, where each integer `a[i]` (1 ≤ a[i] ≤ 10^6) represents the value of each treasure.

## Output Format
- Output a single integer, which is the maximum product of the sums of the two groups.

## Constraints
- 2 ≤ n ≤ 1000
- 1 ≤ a[i] ≤ 10^6

## Example
### Input
```
5
1 2 3 4 5
```

### Output
```
48
```

### Explanation
If we split the array into two groups: {1, 2} and {3, 4, 5}, the sums are 3 and 12 respectively. The product of these sums is 3 * 12 = 36, which is not optimal. The optimal split is {1, 2, 3} and {4, 5}, which results in sums of 6 and 9, giving a product of 54. 

Note that the maximum product occurs when the split results in close to equal sums, thus yielding the highest product.