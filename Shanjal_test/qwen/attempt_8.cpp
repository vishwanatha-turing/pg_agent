Here's a C++14 solution to solve the problem of dividing the kingdom into two equal regions with the most balanced sum difference:

```cpp
#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>

int main() {
    int n;
    std::cin >> n;
    std::vector<int> cities(n);
    
    for (int i = 0; i < n; ++i) {
        std::cin >> cities[i];
    }

    // Sort the city identifiers
    std::sort(cities.begin(), cities.end());

    // Compute the total sum of city identifiers
    long long total_sum = std::accumulate(cities.begin(), cities.end(), 0LL);

    // Calculate the sum of the first n/2 cities
    long long half_sum_1 = std::accumulate(cities.begin(), cities.begin() + n/2, 0LL);

    // Calculate the sum of the last n/2 cities
    long long half_sum_2 = total_sum - half_sum_1;

    // Output the absolute difference
    std::cout << std::abs(half_sum_2 - half_sum_1) << std::endl;

    return 0;
}
```

### Explanation

1. **Input Reading**: We read the number of cities `n` and the city identifiers into a vector `cities`.

2. **Sorting**: We sort the `cities` vector. This helps in creating two balanced regions in terms of sums.

3. **Total Sum Calculation**: We calculate the total sum of all city identifiers using `std::accumulate`.

4. **Half Sum Calculation**: We calculate the sum of the first `n/2` cities (`half_sum_1`). The sum of the remaining cities (`half_sum_2`) is simply the total sum minus `half_sum_1`.

5. **Maximal Sum Difference**: The problem requires the maximal possible sum difference between the two regions, which is achieved by taking the absolute difference between `half_sum_1` and `half_sum_2`.

This solution leverages sorting to easily split the sorted list into two halves, ensuring that the division is both balanced in terms of number of cities and sum difference.