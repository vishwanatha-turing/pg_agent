```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <numeric>
#include <limits>

using namespace std;

// Function to calculate the maximal possible sum difference
int maximalSumDifference(int n, vector<int>& cities) {
    // Calculate total sum of all city identifiers
    long long totalSum = accumulate(cities.begin(), cities.end(), 0LL);

    // Sort cities to facilitate balanced division
    sort(cities.begin(), cities.end());

    // Initialize minimal difference to a large value
    long long minDifference = numeric_limits<long long>::max();

    // Compute the prefix sum
    vector<long long> prefixSum(n + 1, 0);
    for (int i = 0; i < n; ++i) {
        prefixSum[i + 1] = prefixSum[i] + cities[i];
    }

    // Check all possible divisions
    for (int i = 0; i <= n / 2; ++i) {
        long long sumFirstRegion = prefixSum[i];
        long long sumSecondRegion = totalSum - sumFirstRegion;

        // Calculate the difference
        long long difference = abs(sumSecondRegion - sumFirstRegion);

        // Update minimal difference
        minDifference = min(minDifference, difference);
    }

    // Calculate the maximal possible sum difference
    long long maximalDifference = totalSum - 2 * (totalSum - minDifference) / 2;

    return maximalDifference;
}

int main() {
    int n;
    cin >> n;
    vector<int> cities(n);
    for (int i = 0; i < n; ++i) {
        cin >> cities[i];
    }

    int result = maximalSumDifference(n, cities);
    cout << result << endl;

    return 0;
}
```