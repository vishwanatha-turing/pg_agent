#include <bits/stdc++.h>
using namespace std;
 
const int mod = 1000000007;
 
int main() {
    int n;
    cin >> n;
    vector<int> m(n);
    for (int i = 0; i < n; i++) {
        cin >> m[i];
    }
 
    vector<long long> fact(n + 1);
    fact[0] = 1;
    for (int i = 1; i <= n; i++) {
        fact[i] = fact[i - 1] * i % mod;
    }
 
    vector<vector<vector<long long>>> g(n + 2, vector<vector<long long>>(n + 2, vector<long long>(n + 1, 0)));
    vector<vector<long long>> f(n + 2, vector<long long>(n + 2, 0));
 
    for (int l = 1; l <= n + 1; l++) {
        g[l][l - 1][0] = 1;
    }
 
    for (int len = 1; len <= n; len++) {
        for (int l = 1; l + len - 1 <= n; l++) {
            int r = l + len - 1;
            vector<long long> g0(len + 1, 0);
 
            for (int x = 1; x <= len; x++) {
                g0[x] = (g0[x] + g[l][r - 1][x - 1]) % mod;
            }
 
            for (int mid = l + 1; mid <= r; mid++) {
                int L = mid - l;
                for (int x = 0; x <= L; x++) {
                    long long temp = g[l][mid - 1][x] * f[mid][r] % mod;
                    g0[x] = (g0[x] - temp) % mod;
                }
            }
 
            if (r <= m[l - 1]) {
                f[l][r] = 0;
                for (int x = 0; x <= len; x++) {
                    f[l][r] = (f[l][r] + g0[x] * fact[x]) % mod;
                }
                f[l][r] %= mod;
                if (f[l][r] < 0) f[l][r] += mod;
            } else {
                f[l][r] = 0;
            }
 
            for (int x = 0; x <= len; x++) {
                long long val = g0[x];
                if (x == 0) {
                    val = (val - f[l][r]) % mod;
                }
                g[l][r][x] = val % mod;
                if (g[l][r][x] < 0) {
                    g[l][r][x] += mod;
                }
            }
        }
    }
 
    long long ans = 0;
    for (int x = 0; x <= n; x++) {
        ans = (ans + g[1][n][x] * fact[x]) % mod;
    }
    ans %= mod;
    if (ans < 0) ans += mod;
    cout << ans << endl;
 
    return 0;
}