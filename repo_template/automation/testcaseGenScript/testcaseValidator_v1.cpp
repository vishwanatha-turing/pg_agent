#include <bits/stdc++.h>
using namespace std;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int N;
    assert(cin >> N);
    assert(N >= 1 && N <= 1000);
    vector<int> A(N);
    for (int i = 0; i < N; i++) {
        assert(cin >> A[i]);
        assert(A[i] >= -1000 && A[i] <= 1000);
    }
    cin >> ws;
    assert(cin.eof());
    return 0;
}