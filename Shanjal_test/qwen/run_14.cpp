#include <bits/stdc++.h>
using namespace std;

const int MOD = 1000000007;
const int MAXN = 205;

int n, m[MAXN];
long long dp[MAXN][MAXN];  // dp[l][r] = number of valid permutations of [l..r]

bool is_forbidden(int l, int r) {
    return r <= m[l];
}

int main() {
    ios::sync_with_stdio(false);
    cin >> n;
    for (int i = 1; i <= n; ++i)
        cin >> m[i];

    // Initialize dp[l][r] for all intervals
    for (int len = 1; len <= n; ++len) {
        for (int l = 1; l + len - 1 <= n; ++l) {
            int r = l + len - 1;
            if (len == 1) {
                // Base case: single element
                dp[l][r] = 1;
                if (is_forbidden(l, r)) {
                    dp[l][r] = 0;
                }
            } else {
                dp[l][r] = 0;
                // Try every possible pivot k in [l, r]
                for (int k = l; k <= r; ++k) {
                    long long left = (k == l) ? 1 : dp[l][k - 1];
                    long long right = (k == r) ? 1 : dp[k + 1][r];
                    dp[l][r] = (dp[l][r] + left * right) % MOD;
                }
            }

            // If the entire interval [l..r] is forbidden, subtract 1
            if (is_forbidden(l, r)) {
                dp[l][r] = (dp[l][r] - 1 + MOD) % MOD;
            }
        }
    }

    // The final answer is the number of valid permutations of the entire array
    cout << dp[1][n] % MOD << endl;

    return 0;
}