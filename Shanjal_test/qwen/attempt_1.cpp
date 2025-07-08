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

    long long total_sum = std::accumulate(cities.begin(), cities.end(), 0LL);
    long long half_cities = n / 2;

    std::sort(cities.begin(), cities.end());

    long long best_diff = std::abs(std::accumulate(cities.begin(), cities.begin() + half_cities, 0LL) - 
                                   std::accumulate(cities.begin() + half_cities, cities.end(), 0LL));

    std::cout << best_diff << std::endl;

    return 0;
}
```