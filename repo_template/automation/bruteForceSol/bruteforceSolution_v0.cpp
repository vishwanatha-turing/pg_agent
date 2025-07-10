#include <bits/stdc++.h>
using namespace std;
using ll = long long;
const int MAXN = 1000005;
int spf[MAXN];
void sieve(){
    for(int i=0;i<MAXN;i++) spf[i]=i;
    for(int i=2;i*i<MAXN;i++){
        if(spf[i]==i){
            for(int j=i*i;j<MAXN;j+=i)
                if(spf[j]==j) spf[j]=i;
        }
    }
}
vector<int> get_primes(int x){
    vector<int> v;
    while(x>1){
        int p=spf[x];
        v.push_back(p);
        x/=p;
    }
    return v;
}
int K;
vector<int> primes;
int n;
bool dfs_pack(int idx, vector<ll>& bins, int used){
    if(idx==n) return true;
    ll p = primes[idx];
    ll prev = -1;
    for(int i=0;i<used;i++){
        if(bins[i]==prev) continue;
        if(bins[i]*p<=K){
            bins[i]*=p;
            if(dfs_pack(idx+1,bins,used)) return true;
            bins[i]/=p;
            prev=bins[i];
        }
    }
    if(used<idx+1){
        bins[used]=p;
        if(dfs_pack(idx+1,bins,used+1)) return true;
        bins[used]=1;
    }
    return false;
}
int min_bins(vector<int>& v){
    if(v.empty()) return 0;
    primes = v;
    sort(primes.begin(),primes.end(),greater<int>());
    n = primes.size();
    vector<ll> bins(n,1);
    for(int b=1;b<=n;b++){
        fill(bins.begin(),bins.end(),1);
        function<bool(int,int)> dfs = [&](int idx,int used){
            if(idx==n) return true;
            ll p = primes[idx];
            ll prev = -1;
            for(int i=0;i<used;i++){
                if(bins[i]==prev) continue;
                if(bins[i]*p<=K){
                    bins[i]*=p;
                    if(dfs(idx+1,used)) return true;
                    bins[i]/=p;
                    prev=bins[i];
                }
            }
            if(used<b){
                bins[used]=p;
                if(dfs(idx+1,used+1)) return true;
                bins[used]=1;
            }
            return false;
        };
        if(dfs(0,0)) return b;
    }
    return n;
}
int main(){
    ios::sync_with_stdio(false);
    cin.tie(NULL);
    sieve();
    int t;
    if(!(cin>>t))return 0;
    while(t--){
        int x,y,k;
        cin>>x>>y>>k;
        if(x==y){
            cout<<0<<"\n";
            continue;
        }
        int g = __gcd(x,y);
        int a = y/g;
        int b = x/g;
        vector<pair<int,int>> fa, fb;
        int ta=a, tb=b;
        bool ok=true;
        vector<int> pa, pb;
        pa = get_primes(ta);
        pb = get_primes(tb);
        for(int p:pa) if(p>k) ok=false;
        for(int p:pb) if(p>k) ok=false;
        if(!ok){
            cout<<-1<<"\n"; continue;
        }
        K = k;
        int ma = min_bins(pa);
        int mb = min_bins(pb);
        cout<<ma+mb<<"\n";
    }
    return 0;
}