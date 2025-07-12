#include <bits/stdc++.h>
using namespace std;

const int MOD = 1e9 + 7;

int main() {
    int n;
    cin >> n;
    vector<int> m(n);
    for (int i = 0; i < n; ++i) {
        cin >> m[i];
    }

    long long factorial[201];
    factorial[0] = 1;
    for (int i = 1; i <= n; ++i) {
        factorial[i] = factorial[i - 1] * i % MOD;
    }

    long long dp[201];
    dp[0] = 1;

    for (int i = 1; i <= n; ++i) {
        long long total = factorial[i];
        for (int l = 1; l <= i; ++l) {
            if (m[l - 1] >= i) {
                // Forbidden interval [l, i]
                long long contrib = dp[l - 1] * factorial[i - l + 1] % MOD;
                total = (total - contrib + MOD) % MOD;
            }
        }
        dp[i] = total;
    }

    cout << dp[n] << endl;
    return 0;
}