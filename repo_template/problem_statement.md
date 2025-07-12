# Festival Experience Segmentation

A festival organizer records each attendee’s emotional experience as an integer: negative values for unpleasant moments, positive values for happy moments, and zero for neutral feelings. To encourage sharing and small-group activities, the organizer wants to divide the sequence of recorded experiences into contiguous segments. The “score” of a segment is the sum of its experience values, and the overall festival score is the product of the scores of all segments.  

Your task is to help the organizer choose how to split the list of experiences into one or more contiguous segments so that the overall festival score is as large as possible. Since the numbers can get very large, report the maximum possible score modulo 10^9 + 7.

## Input Format

The first line contains a single integer N, the number of recorded experiences.  
The second line contains N space-separated integers A[1], A[2], …, A[N], where A[i] is the i-th experience value.

## Output Format

Output a single integer: the maximum possible product of the segment sums, taken modulo 10^9 + 7.

## Constraints

• 1 ≤ N ≤ 1000  
• –1000 ≤ A[i] ≤ 1000  

## Example

Input  
```
5
2 -1 3 0 -2
```

Output  
```
12
```

Explanation  
One optimal way is to split into segments `[2]`, `[-1]`, `[3]`, and `[0, -2]`.  
Their sums are 2, –1, 3, and –2, and the product is 2 × (–1) × 3 × (–2) = 12, which is the maximum achievable.