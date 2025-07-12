# Problem Statement: Prime Hash

In the world of cryptography, hashing is a fundamental concept that involves transforming input data into a fixed-size string of characters, which is typically a sequence of numbers. In this problem, you are tasked with creating a unique hash for a sequence of numbers using prime numbers and mathematical transformations.

## Problem Description

You are given a sequence of integers. Your task is to generate a unique hash value for the sequence using the following method:

1. For each integer in the sequence, find the smallest prime number that is greater than or equal to the integer.
2. Compute the product of these prime numbers.
3. Given an integer `M`, find the remainder when this product is divided by `M`.

The challenge is to efficiently compute this hash value given the constraints.

## Input Format

- The first line contains two integers, `N` and `M`:
  - `N` (1 ≤ N ≤ 10^5) is the number of integers in the sequence.
  - `M` (1 ≤ M ≤ 10^9) is the modulus value.
- The second line contains `N` space-separated integers, `a[i]` (1 ≤ a[i] ≤ 10^6), representing the sequence.

## Output Format

- Output a single integer that is the hash value calculated as described above.

## Constraints

- The sequence contains up to 100,000 integers.
- The values in the sequence can be as large as 1,000,000.
- The modulus value `M` can be as large as 1 billion.

## Example Test Cases

### Example 1

**Input:**

```
5 100
4 6 8 10 12
```

**Output:**

```
84
```

**Explanation:**

- The smallest primes greater than or equal to each number are: 5, 7, 11, 11, 13.
- The product of these primes is 5 * 7 * 11 * 11 * 13 = 55385.
- The hash value is 55385 % 100 = 85.

### Example 2

**Input:**

```
3 1000
2 3 5
```

**Output:**

```
30
```

**Explanation:**

- The smallest primes greater than or equal to each number are: 2, 3, 5.
- The product of these primes is 2 * 3 * 5 = 30.
- The hash value is 30 % 1000 = 30.

## Notes

- You may need to use efficient algorithms or precomputations (such as the Sieve of Eratosthenes) to handle large input sizes and constraints.
- Consider edge cases, such as when all numbers in the sequence are the same or when some of the numbers are already prime.

Your task is to implement the solution that calculates the hash value as efficiently as possible.