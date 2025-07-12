#include <bits/stdc++.h>
using namespace std;

typedef long long ll;
const int MOD = 1e9 + 7;
const int MAXN = 210;

ll dp[MAXN];
ll fact[MAXN];
vector<int> ends_at[MAXN];

int main() {
    ios::sync_with_stdio(false);
    cin.tie(0);
    int n;
    cin >> n;
    fact[0] = 1;
    for (int i = 1; i <= n; ++i) {
        fact[i] = fact[i-1] * i % MOD;
    }
    int m[MAXN];
    for (int i = 1; i <= n; ++i) {
        cin >> m[i];
    }
    // Precompute for each position i, the list of l such that [l..i] is forbidden
    for (int i = 1; i <= n; ++i) {
        for (int l = 1; l <= i; ++l) {
            if (m[l] >= i) {
                ends_at[i].push_back(l);
            }
        }
    }
    dp[0] = 1;
    for (int i = 1; i <= n; ++i) {
        dp[i] = fact[i];
        for (int l : ends_at[i]) {
            ll term = dp[l-1] * fact[i - l + 1] % MOD;
            dp[i] = (dp[i] - term + MOD) % MOD;
        }
    }
    cout << dp[n] % MOD << endl;
    return 0;
}