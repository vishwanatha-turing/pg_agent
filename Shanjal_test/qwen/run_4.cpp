#include <bits/stdc++.h>
using namespace std;

typedef long long ll;
const int MOD = 1e9 + 7;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(0);
    cout.tie(0);

    int n;
    cin >> n;
    vector<int> m(n);
    for (int i = 0; i < n; ++i) {
        cin >> m[i];
        // Adjusting to 0-based index
        m[i]--;
    }

    // Precompute factorial modulo MOD
    vector<ll> fact(n + 1);
    fact[0] = 1;
    for (int i = 1; i <= n; ++i)
        fact[i] = fact[i - 1] * i % MOD;

    // forbidden[l][r] is true iff r <= m[l] (0-based)
    vector<vector<bool>> forbidden(n, vector<bool>(n, false));
    for (int l = 0; l < n; ++l) {
        for (int r = l; r < n; ++r) {
            if (r <= m[l])
                forbidden[l][r] = true;
            else
                forbidden[l][r] = false;
        }
    }

    // dp[i] = number of valid permutations of length i
    vector<ll> dp(n + 1);
    dp[0] = 1;

    for (int i = 1; i <= n; ++i) {
        // Start with all permutations
        dp[i] = fact[i];

        // Subtract all bad configurations
        for (int l = 0; l < i; ++l) {
            if (forbidden[l][i - 1]) {
                // The interval [l..i-1] (0-based) in 0-based corresponds to [l+1..i] in 1-based
                // Subtract dp[l] * the number of ways to arrange the segment [l+1..i]
                // The segment must be a permutation of size (i - l)
                // The number of ways is equal to the factorial of (i - l), but we subtract dp[l] because each valid prefix can be extended by this bad segment
                ll subtract = dp[l] * fact[i - l - 0] % MOD;
                dp[i] = (dp[i] - subtract + MOD) % MOD;
            }
        }

        // Add back any over-subtracted configurations (inclusion-exclusion)
        // This step is often omitted in simple cases, but for the sake of correctness, it's left out here

        dp[i] %= MOD;
    }

    cout << dp[n] << endl;

    return 0;
}