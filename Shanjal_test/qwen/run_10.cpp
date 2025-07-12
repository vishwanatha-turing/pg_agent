#include <bits/stdc++.h>
using namespace std;

const int MOD = 1000000007;
const int MAXN = 205;

int main() {
    int n;
    cin >> n;
    vector<int> m(n + 1); // m[1..n]
    for (int i = 1; i <= n; ++i) {
        cin >> m[i];
    }

    // Precompute factorials modulo MOD
    vector<long long> fact(n + 1);
    fact[0] = 1;
    for (int i = 1; i <= n; ++i) {
        fact[i] = fact[i - 1] * i % MOD;
    }

    // dp[i] = number of valid permutations of size i
    vector<long long> dp(n + 1, 0);
    dp[0] = 1; // empty permutation

    for (int i = 1; i <= n; ++i) {
        dp[i] = fact[i]; // total permutations
        // Subtract all permutations that have at least one forbidden interval ending at i
        for (int l = 1; l <= i; ++l) {
            if (m[l] >= i) {
                // Forbidden interval [l, i]
                long long val = dp[l - 1] * fact[i - l + 1] % MOD;
                dp[i] = (dp[i] - val + MOD) % MOD;
            }
        }
        dp[i] = dp[i] % MOD;
    }

    cout << dp[n] << endl;
    return 0;
}