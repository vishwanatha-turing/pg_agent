Here's a C++14 solution to solve the problem of dividing the kingdom into two regions with equal number of cities and a minimal sum difference:

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <numeric>

int main() {
    int n;
    std::cin >> n;

    std::vector<int> cities(n);
    for (int i = 0; i < n; ++i) {
        std::cin >> cities[i];
    }

    // Calculate the total sum of all city identifiers
    int total_sum = std::accumulate(cities.begin(), cities.end(), 0);

    // Each region must have n/2 cities
    int half_cities = n / 2;

    // We need to find two subsets of size n/2 with minimal sum difference
    // This is equivalent to finding a subset with sum closest to total_sum / 2
    int target_sum = total_sum / 2;

    // Use dynamic programming to find the closest possible sum to target_sum
    std::vector<int> dp(target_sum + 1, 0);

    for (int i = 0; i < n; ++i) {
        for (int j = target_sum; j >= cities[i]; --j) {
            dp[j] = std::max(dp[j], dp[j - cities[i]] + cities[i]);
        }
    }

    // Find the best possible sum for one of the regions
    int best_sum = dp[target_sum];

    // Calculate the sum of the other region
    int other_sum = total_sum - best_sum;

    // Calculate the absolute difference
    int max_difference = std::abs(other_sum - best_sum);

    std::cout << max_difference << std::endl;

    return 0;
}
```

This solution uses a dynamic programming approach to find the subset of city identifiers whose sum is closest to half of the total sum. The dynamic programming table `dp` is used to track the best achievable sum up to `target_sum`. After computing the closest possible sum `best_sum` to `target_sum`, the difference between `best_sum` and `total_sum - best_sum` is computed and returned as the result.

Note: The problem implicitly assumes that the graph (cities and roads) forms a single cycle, but since we're dealing with sums and identifiers without explicit roads, this dynamic programming approach directly addresses the partitioning by identifiers.