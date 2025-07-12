#include <bits/stdc++.h>
using namespace std;

const int MOD = 1e9 + 7;
const int MAXN = 210;

int n;
int m[MAXN];
long long fact[MAXN];
long long dp[MAXN];

int main() {
    ios::sync_with_stdio(false);
    cin >> n;
    for (int i = 1; i <= n; ++i) {
        cin >> m[i];
    }

    // Precompute factorials
    fact[0] = 1;
    for (int i = 1; i <= n; ++i) {
        fact[i] = fact[i - 1] * i % MOD;
    }

    // Initialize dp array
    dp[0] = 1;

    for (int i = 1; i <= n; ++i) {
        // Start with all permutations
        dp[i] = fact[i];

        // Subtract all permutations that have a forbidden interval ending at i
        for (int l = 1; l <= i; ++l) {
            if (i <= m[l]) {
                // Check if [l..i] is a forbidden interval
                if (l > i) continue;
                // The number of permutations where [l..i] is a forbidden interval
                // is dp[l-1] * (number of permutations of elements l..i)
                // but since the interval [l..i] must exactly be l..i, the number of ways is 1 * (i-l+1)! ?
                // Or wait, the elements in [l..i] must be exactly {l, ..., i}, but they can be in any order
                // So the number of ways to permute them is (i-l+1)! 
                // But we need to subtract all permutations that have this interval
                // So the term to subtract is dp[l-1] * (i-l+1)! 
                // But wait, the total elements in the permutation is i, and we are considering permutations of size i
                // So the elements not in [l..i] are in the prefix [1..l-1], which must be a valid permutation of those elements
                // and the elements in [l..i] are exactly {l..i} in any order
                // So the number of such permutations is dp[l-1] * ( (i-l+1)! ) * C(i, l-1) ? No, not sure.
                // But in our model, we assume that the prefix up to l-1 is a valid permutation of size l-1
                // and the suffix from l to i is any permutation of {l..i}
                // So the total ways for this is dp[l-1] * (i-l+1)! 
                // But wait, the total elements up to i is l-1 elements + (i-l+1) elements = i elements.
                // So the elements in the suffix must be exactly {l..i}, which are i-l+1 elements.
                // The total number of permutations of size i that have [l..i] as a forbidden interval is dp[l-1] * (i-l+1)! 
                // Because the prefix is valid permutation of size l-1 (using elements 1..l-1), and the suffix is any permutation of l..i
                // So we subtract this from dp[i]
                long long term = dp[l - 1] * fact[i - l + 1] % MOD;
                dp[i] = (dp[i] - term + MOD) % MOD;
            }
        }
    }

    cout << dp[n] << endl;
    return 0;
}