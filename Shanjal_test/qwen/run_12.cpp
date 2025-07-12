#include <bits/stdc++.h>
using namespace std;

const int MOD = 1e9 + 7;
const int MAXN = 210;

int n, m[MAXN];
long long fact[MAXN];
long long dp[MAXN];

int main() {
    ios::sync_with_stdio(false);
    cin.tie(0);
    cin >> n;
    for (int i = 1; i <= n; ++i) {
        cin >> m[i];
    }
    
    // Precompute factorials modulo MOD
    fact[0] = 1;
    for (int i = 1; i <= n; ++i) {
        fact[i] = fact[i - 1] * i % MOD;
    }
    
    dp[0] = 1; // Empty permutation
    
    for (int i = 1; i <= n; ++i) {
        // Total permutations of size i
        long long total = fact[i];
        
        // Subtract invalid permutations that have at least one forbidden interval ending at i
        for (int l = 1; l <= i; ++l) {
            if (m[l] >= i) {
                // Forbidden interval [l..i]
                if (l - 1 >= 0) {
                    long long contrib = dp[l - 1] * fact[i - l] % MOD;
                    total = (total - contrib + MOD) % MOD;
                }
            }
        }
        
        dp[i] = total;
    }
    
    cout << dp[n] << endl;
    
    return 0;
}