Here's the C++14 code solution for the "Dividing the Kingdom" problem. The approach involves finding the best possible division of the cities into two equal parts such that the sum difference between the two regions is maximized. The solution relies on sorting the city identifiers and then strategically dividing them to achieve the best balance.

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <numeric>
#include <cmath>

int main() {
    int n;
    std::cin >> n;
    std::vector<int> cities(n);

    for (int i = 0; i < n; ++i) {
        std::cin >> cities[i];
    }

    // Sort the city identifiers
    std::sort(cities.begin(), cities.end());

    // Calculate the total sum of all city identifiers
    long long totalSum = std::accumulate(cities.begin(), cities.end(), 0LL);

    // We will try to divide the sorted array into two equal parts
    // The first half will be one region and the second half another region
    // This will help us ensure that the number of cities in both regions are equal

    int half = n / 2;
    long long sumRegion1 = std::accumulate(cities.begin(), cities.begin() + half, 0LL);
    long long sumRegion2 = totalSum - sumRegion1;

    // Calculate the difference
    long long diff = std::abs(sumRegion1 - sumRegion2);

    // Since we need the maximum possible sum difference, and the array is sorted,
    // the optimal division is the one directly split by half
    std::cout << diff << std::endl;

    return 0;
}
```

### Explanation

1. **Sorting**: The city identifiers are sorted. This is important because it allows us to consider the smallest and largest elements in two different regions to maximize the sum difference.

2. **Total Sum Calculation**: Compute the total sum of city identifiers. This helps in determining the sum of the second region once the first region's sum is known.

3. **Split the Sorted Array**: By splitting the sorted array into two halves, you ensure that each region has an equal number of cities. This is guaranteed since `n` is even.

4. **Calculate and Output the Difference**: Calculate the sum of each region and then determine the absolute difference. The sorted nature of the array ensures that this difference is maximized.

This solution efficiently computes the desired result in `O(n log n)` time complexity due to sorting, and `O(n)` for the sum calculations. This is suitable given the constraint of `n` up to 100,000.