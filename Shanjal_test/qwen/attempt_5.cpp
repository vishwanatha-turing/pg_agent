```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <numeric>
#include <limits>

int main() {
    int n;
    std::cin >> n;

    std::vector<int> cities(n);
    for (int i = 0; i < n; ++i) {
        std::cin >> cities[i];
    }

    // Sort the cities to evaluate potential balanced groups
    std::sort(cities.begin(), cities.end());

    // The sum of all identifiers
    int total_sum = std::accumulate(cities.begin(), cities.end(), 0);

    // We are looking to partition cities into two groups of n/2
    int half_n = n / 2;
    int min_difference = std::numeric_limits<int>::max();

    // Evaluate the sum difference for each possible split
    for (int i = 0; i <= half_n; ++i) {
        // Sum of one half
        int sum_first_half = std::accumulate(cities.begin(), cities.begin() + i, 0)
                           + std::accumulate(cities.end() - (half_n - i), cities.end(), 0);

        // Sum of the second half implicitly
        int sum_second_half = total_sum - sum_first_half;

        // Compute the absolute difference
        int difference = std::abs(sum_first_half - sum_second_half);

        // We're interested in the minimal possible difference
        min_difference = std::min(min_difference, difference);
    }

    // Output the minimal possible difference
    std::cout << min_difference << std::endl;

    return 0;
}
```