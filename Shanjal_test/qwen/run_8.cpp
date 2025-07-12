#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const int MOD = 1e9 + 7;

int n;
vector<int> m;

bool isForbiddenSegment(const vector<int>& p, const vector<vector<int>>& forbiddenForR, int current_pos) {
    for (int l : forbiddenForR[current_pos]) {
        int current_min = p[l - 1];
        int current_max = p[l - 1];
        for (int i = l - 1; i < current_pos; ++i) {
            if (p[i] < current_min) current_min = p[i];
            if (p[i] > current_max) current_max = p[i];
        }
        if (current_min == l && current_max == current_pos) {
            return true;
        }
    }
    return false;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(0);
    cout.tie(0);

    cin >> n;
    m.resize(n + 2, 0);
    for (int i = 1; i <= n; ++i) {
        cin >> m[i];
    }

    vector<vector<int>> forbiddenForR(n + 2); // forbiddenForR[r] contains all l such that [l, r] is forbidden
    for (int r = 1; r <= n; ++r) {
        for (int l = 1; l <= r; ++l) {
            if (m[l] >= r) {
                forbiddenForR[r].push_back(l);
            }
        }
    }

    ll ans = 0;
    vector<bool> used(n + 2, false);
    vector<int> p;

    function<void(int)> backtrack = [&](int pos) {
        if (pos == n) {
            ans = (ans + 1) % MOD;
            return;
        }

        for (int i = 1; i <= n; ++i) {
            if (used[i]) continue;
            used[i] = true;
            p.push_back(i);
            int current_pos = pos + 1;

            bool valid = true;
            for (int l : forbiddenForR[current_pos]) {
                int current_min = i;
                int current_max = i;
                for (int k = l - 1; k < current_pos; ++k) {
                    if (p[k] < current_min) current_min = p[k];
                    if (p[k] > current_max) current_max = p[k];
                }
                if (current_min == l && current_max == current_pos) {
                    valid = false;
                    break;
                }
            }

            if (valid) {
                backtrack(pos + 1);
            }

            p.pop_back();
            used[i] = false;
        }
    };

    backtrack(0);
    cout << ans << endl;
    return 0;
}