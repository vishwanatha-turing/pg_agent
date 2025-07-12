#include <bits/stdc++.h>
using namespace std;

const int MOD = 1e9 + 7;
const int MAXN = 205;

int n;
int m[MAXN];
long long fact[MAXN];
long long dp[MAXN];

int main() {
    cin >> n;
    for (int i = 1; i <= n; ++i) {
        cin >> m[i];
    }

    fact[0] = 1;
    for (int i = 1; i <= n; ++i) {
        fact[i] = fact[i - 1] * i % MOD;
    }

    dp[0] = 1;
    for (int i = 1; i <= n; ++i) {
        dp[i] = fact[i];
        for (int l = 1; l <= i; ++l) {
            if (m[l] >= i) {
                long long ways = dp[l - 1] * fact[i - l] % MOD;
                dp[i] = (dp[i] - ways + MOD) % MOD;
            }
        }
        dp[i] = dp[i] % MOD;
    }

    cout << dp[n] << endl;

    return 0;
}