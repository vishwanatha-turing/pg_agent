# Problem Title: The Enigma of Dynamic Illumination

### Problem Statement

You are appointed as the chief architect of a futuristic city. The city is built on a grid with \( n \times n \) intersections. Each intersection is equipped with a dynamic light module that can emit light in one of three colors: Red, Green, or Blue. The city council has imposed the following illumination policy:

1. **Illumination Rule**: Every row and column must have exactly one intersection illuminated with Red and one with Green. The remaining intersections in each row and column must be Blue.
2. **Visibility Constraint**: No two Red lights can be in the same diagonal (both primary or secondary) of the grid. Similarly, no two Green lights can be in the same diagonal.
3. **Harmony Requirement**: For any chosen \( k \times k \) subgrid, the number of Red lights must be equal to the number of Green lights, modulo 2.

Given \( n \), your task is to configure the grid in a way that satisfies all the above conditions.

### Input

- A single integer \( n \) (1 ≤ \( n \) ≤ 100,000), the size of the grid.

### Output

- Output the configuration of the grid as \( n \) lines, each containing \( n \) characters ('R', 'G', or 'B'), representing the color of the light at each intersection.
- Multiple valid configurations are possible. Any correct configuration will be accepted.

### Constraints and Edge Cases

- Adversarial inputs are designed to break naive O(n^2) approaches.
- Consider precision errors in logic, especially with large \( n \).
- Ensure that your solution is efficient enough to handle the upper bounds of \( n \) within the time limit.

### Example

**Input**

```
5
```

**Output**

```
RBBGB
GBRBB
BRGBB
BBGBR
BBGRB
```

### Explanation

- Each row and column have exactly one 'R' and one 'G'.
- No two 'R's or 'G's are on the same diagonal.
- The \( 2 \times 2 \) subgrid rule holds for the chosen configuration.
- Multiple outputs are possible, and this is just one valid configuration.

### Evaluation Criteria

- Binary scoring: Solutions are marked correct or incorrect.
- Hidden edge cases will test the robustness of the solution.
- Submissions using naive methods or failing hidden constraints will not pass.

### Notes

- The problem is suitable for advanced competitions, with emphasis on combinatorial insight and efficient computation strategies.
- The challenge lies in balancing the constraints and efficiently computing a valid configuration for large grids.