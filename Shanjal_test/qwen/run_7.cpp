#include <bits/stdc++.h>
using namespace std;

const int MOD = 1000000007;
const int MAXN = 210;

int dp[MAXN][1 << 8]; // Simplified for illustration
int min_val[MAXN][MAXN];
int max_val[MAXN][MAXN];

int main() {
    int n;
    cin >> n;
    vector<int> m(n);
    for (int i = 0; i < n; ++i) {
        cin >> m[i];
    }

    // Initialize dp array
    vector<vector<long long>> dp(n + 1, vector<long long>(1 << n, 0));
    dp[0][0] = 1;

    for (int i = 0; i < n; ++i) {
        for (int mask = 0; mask < (1 << n); ++mask) {
            if (dp[i][mask] == 0) continue;
            for (int j = 0; j < n; ++j) {
                if ((mask & (1 << j)) == 0) {
                    int new_mask = mask | (1 << j);
                    // Update min and max for all intervals ending at i+1
                    for (int l = 0; l <= i + 1; ++l) {
                        if (l == i + 1) {
                            min_val[l][i + 1] = j + 1;
                            max_val[l][i + 1] = j + 1;
                        } else {
                            min_val[l][i + 1] = min(min_val[l][i], j + 1);
                            max_val[l][i + 1] = max(max_val[l][i], j + 1);
                        }
                    }

                    bool valid = true;
                    for (int l = 0; l <= i; ++l) {
                        if (i + 1 <= m[l]) {
                            if (min_val[l][i + 1] == l + 1 && max_val[l][i + 1] == i + 1) {
                                valid = false;
                                break;
                            }
                        }
                    }

                    if (valid) {
                        dp[i + 1][new_mask] = (dp[i + 1][new_mask] + dp[i][mask]) % MOD;
                    }
                }
            }
        }
    }

    long long result = 0;
    for (int mask = 0; mask < (1 << n); ++mask) {
        result = (result + dp[n][mask]) % MOD;
    }

    cout << result << endl;
    return 0;
}