F. Small Operations

time limit per test: 3 seconds
memory limit per test: 256 megabytes

Given an integer x and an integer k. In one operation, you can perform one of two actions:

choose an integer 1≤a≤k and assign x=x*a;
choose an integer 1≤a≤k and assign x=x/a, where the value of x/a must be an integer.
Find the minimum number of operations required to make the number x equal to y, or determine that it is impossible.

Input

The first line of the input contains one integer t (1≤t≤10**4) — the number of test cases.

The only line of each test case contains three integers x, y and k(1 ≤ x,y,k ≤ 10**6).

It is guaranteed that the sum of x and the sum of y across all test cases does not exceed 10**8.

Output

For each test case, output −1 if it is impossible to achieve x=y
using the given operations, and the minimum number of required operations otherwise.

Example

Input
8
4 6 3
4 5 3
4 6 2
10 45 3
780 23 42
11 270 23
1 982800 13
1 6 2

Output
2
-1
-1
3
3
3
6
-1

