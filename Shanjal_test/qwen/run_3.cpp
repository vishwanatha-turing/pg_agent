#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const int MOD = 1e9 + 7;
const int MAXN = 205;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(0);
    cout.tie(0);

    int n;
    cin >> n;
    vector<int> m(n);
    for (int i = 0; i < n; ++i) {
        cin >> m[i];
    }

    // Precompute factorials modulo MOD
    vector<ll> fact(n + 1);
    fact[0] = 1;
    for (int i = 1; i <= n; ++i) {
        fact[i] = (fact[i - 1] * i) % MOD;
    }

    // dp[i] = number of valid permutations of length i
    vector<ll> dp(n + 1, 0);
    dp[0] = 1;

    for (int i = 1; i <= n; ++i) {
        dp[i] = fact[i]; // Start with all permutations

        // Subtract permutations that contain at least one forbidden interval ending at i
        for (int a = 1; a <= i; ++a) {
            if (m[a - 1] >= i) {
                // Forbidden interval [a..i]
                ll bad = (dp[a - 1] * fact[i - a]) % MOD;
                dp[i] = (dp[i] - bad + MOD) % MOD;
            }
        }

        dp[i] = (dp[i] + MOD) % MOD;
    }

    cout << dp[n] << "\n";
    return 0;
}