## Problem Statement

You are given an integer $n$, and you must count how many **permutations** $p$ of the array $[1, 2, ........, n]$ satisfy the following condition:

> For every index $l$ (from 1 to $n$), and for every $r$ such that $l \leq r \leq m_l$, the subarray $[p_l, p_{l+1}, ........, p_r]$ is **not** a permutation of $[l, l+1, ........, r]$.

In simpler terms: For each segment starting at index $l$ and ending at any index $r$ up to $m_l$, that segment in the permutation **must not** be exactly a rearrangement of the natural numbers from $l$ to $r$.

Since the result can be large, output the answer modulo $10^9 + 7$.

---

## Input Format

* The first line contains a single integer $n$ ( $1 \leq n \leq 200$ )  the size of the permutation.
* The second line contains $n$ integers $m_1, m_2, ........, m_n$ ( $0 \leq m_i \leq n$ ).


---

## Output Format

* Output a single integer  the number of valid permutations satisfying the given condition, modulo $10^9 + 7$.

---

## Examples

### Example 1

**Input**

```
3
1 2 3
```

**Output**

```
2
```

**Explanation**
The valid permutations are `[2, 3, 1]` and `[3, 1, 2]`.

---

### Example 2

**Input**

```
5
2 4 3 4 5
```

**Output**

```
38
```

---

### Example 3

**Input**

```
5
5 1 1 1 1
```

**Output**

```
0
```
