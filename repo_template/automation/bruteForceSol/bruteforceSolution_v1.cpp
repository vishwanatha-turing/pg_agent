#include <bits/stdc++.h>
using namespace std;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    const int MOD = 1000000007;
    int N;
    cin >> N;
    vector<long long> A(N+1), pref(N+1);
    for(int i=1;i<=N;i++){
        cin>>A[i];
        pref[i]=pref[i-1]+A[i];
    }
    vector<bool> has_pos(N+1,false), has_neg(N+1,false), has_zero(N+1,false);
    vector<double> pos_log(N+1, -1e300), neg_log(N+1, 1e300);
    vector<int> pos_mod(N+1,0), neg_mod(N+1,0);
    has_pos[0]=true; pos_log[0]=0; pos_mod[0]=1;
    for(int i=1;i<=N;i++){
        for(int j=0;j<i;j++){
            long long S = pref[i] - pref[j];
            if(S>0){
                double lg = log((double)S);
                if(has_pos[j]){
                    double nl = pos_log[j] + lg;
                    int nm = (int)((1LL*pos_mod[j]* (S%MOD))%MOD);
                    if(!has_pos[i] || nl > pos_log[i]){
                        has_pos[i]=true;
                        pos_log[i]=nl;
                        pos_mod[i]=nm;
                    }
                }
                if(has_neg[j]){
                    double nl = neg_log[j] + lg;
                    int nm = (int)((1LL*neg_mod[j]* (S%MOD))%MOD);
                    if(!has_neg[i] || nl < neg_log[i]){
                        has_neg[i]=true;
                        neg_log[i]=nl;
                        neg_mod[i]=nm;
                    }
                }
            } else if(S<0){
                double lg = log((double)(-S));
                int s_mod = (int)((-S)%MOD);
                if(s_mod<0) s_mod+=MOD;
                if(has_pos[j]){
                    double nl = pos_log[j] + lg;
                    int nm = (int)(1LL * pos_mod[j] * s_mod % MOD);
                    nm = (MOD - nm) % MOD;
                    if(!has_neg[i] || nl < neg_log[i]){
                        has_neg[i]=true;
                        neg_log[i]=nl;
                        neg_mod[i]=nm;
                    }
                }
                if(has_neg[j]){
                    double nl = neg_log[j] + lg;
                    int nm = (int)(1LL * neg_mod[j] * s_mod % MOD);
                    nm = (MOD - nm) % MOD;
                    if(!has_pos[i] || nl > pos_log[i]){
                        has_pos[i]=true;
                        pos_log[i]=nl;
                        pos_mod[i]=nm;
                    }
                }
            } else {
                if(has_pos[j] || has_neg[j] || has_zero[j]){
                    has_zero[i] = true;
                }
            }
        }
    }
    if(has_pos[N]){
        cout << pos_mod[N];
    } else if(has_zero[N]){
        cout << 0;
    } else {
        cout << neg_mod[N];
    }
    return 0;
}