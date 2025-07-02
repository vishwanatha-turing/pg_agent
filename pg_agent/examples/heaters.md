
# Heater Radius Problem

## Problem Statement

**Winter is coming!**  
During the contest, your first job is to design a standard heater with a fixed warm radius to warm all the houses.

Every house can be warmed as long as the house is within the heater's warm radius range.

You are given two integer arrays:

- `houses`: the positions of houses on a horizontal line
- `heaters`: the positions of heaters on the same line

Return the **minimum radius** standard of heaters so that all the houses can be warmed.  
**Note:** All the heaters follow the same radius standard.

---

## Examples

### Example 1

**Input:**

```python
houses = [1, 2, 3]
heaters = [2]
````

**Output:**

```
1
```

**Explanation:**
The only heater was placed at position `2`, and if we use radius `1`, then all the houses can be warmed.

---

### Example 2

**Input:**

```python
houses = [1, 2, 3, 4]
heaters = [1, 4]
```

**Output:**

```
1
```

**Explanation:**
The heaters are at positions `1` and `4`. Using a radius of `1` allows them to warm all houses.

---

### Example 3

**Input:**

```python
houses = [1, 5]
heaters = [2]
```

**Output:**

```
3
```

**Explanation:**
To warm both house `1` and house `5` with a single heater at position `2`, the radius must be `3`.

---

## Constraints

* `1 <= houses.length, heaters.length <= 3 * 10^4`
* `1 <= houses[i], heaters[i] <= 10^9`