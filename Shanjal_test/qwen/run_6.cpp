#include <bits/stdc++.h>
using namespace std;
const int MOD = 1000000007;

int n;
vector<int> m;
vector<vector<long long>> dp;
vector<vector<vector<pair<int, int>>>> minmax;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(0);

    cin >> n;
    m.resize(n + 1);
    for (int i = 1; i <= n; ++i) {
        cin >> m[i];
    }

    // dp[i] = number of valid permutations of length i
    dp.resize(n + 1);
    minmax.resize(n + 1, vector<vector<pair<int, int>>>(n + 2));

    // Initialize dp[0] with one valid permutation (empty)
    dp[0] = 1;
    minmax[0].clear();

    for (int i = 1; i <= n; ++i) {
        // For each permutation of length i-1, try adding a new number
        for (int used = 0; used < (1 << n); ++used) {
            if (__builtin_popcount(used) != i - 1) continue;
            long long count = dp[used];
            if (count == 0) continue;

            for (int num = 1; num <= n; ++num) {
                if ((used & (1 << (num - 1))) != 0) continue;

                // Compute new min and max for intervals ending at i
                vector<int> curr_min(i + 1, 0);
                vector<int> curr_max(i + 1, 0);

                for (int l = 1; l < i; ++l) {
                    curr_min[l] = min(minmax[used][i - 1][l].first, num);
                    curr_max[l] = max(minmax[used][i - 1][l].second, num);
                }
                curr_min[i] = curr_max[i] = num;

                // Check all intervals [l, i] where i <= m[l]
                bool valid = true;
                for (int l = 1; l <= i && l <= m[i]; ++l) {
                    if (curr_min[l] == l && curr_max[l] == i) {
                        valid = false;
                        break;
                    }
                }

                if (valid) {
                    int new_used = used | (1 << (num - 1));
                    dp[new_used] = (dp[new_used] + count) % MOD;
                    for (int l = 1; l <= i; ++l) {
                        minmax[new_used][i][l] = {curr_min[l], curr_max[l]};
                    }
                }
            }
        }
    }

    cout << dp[(1 << n) - 1] << endl;
    return 0;
}