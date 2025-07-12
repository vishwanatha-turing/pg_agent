#include <bits/stdc++.h>
using namespace std;
int main() {
    srand(0);
    int T = 80;
    vector<int> same_vals = {0,1,-1,1000,-1000,5,-5,999};
    vector<int> primes = {
        2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,
        73,79,83,89,97,101,103,107,109,113,127,131,137,139,149,151,
        157,163,167,173,179,181,191,193,197,199,211,223,227,229
    };
    for(int t=1; t<=T; t++){
        ofstream fout(to_string(t) + ".in");
        int N;
        vector<int> A;
        if(t <= 3) {
            N = 1;
            A.resize(1);
            if(t==1) A[0] = 1000;
            else if(t==2) A[0] = -1000;
            else A[0] = 0;
        }
        else if(t <= 11) {
            N = 50;
            A.assign(50, same_vals[t-4]);
        }
        else if(t <= 26) {
            N = 50;
            A.resize(50);
            int idx = t - 12;
            if(idx == 0){
                for(int i=0;i<50;i++) A[i] = (i%2==0?1000:-1000);
            } else if(idx == 1){
                for(int i=0;i<50;i++) A[i] = (i%2==0?-1000:1000);
            } else if(idx == 2){
                for(int i=0;i<50;i++) A[i] = (i%2==0?1:-1);
            } else if(idx == 3){
                for(int i=0;i<50;i++) A[i] = (i%2==0?-1:1);
            } else if(idx == 4){
                for(int i=0;i<50;i++) A[i] = i;
            } else if(idx == 5){
                for(int i=0;i<50;i++) A[i] = i+1;
            } else if(idx == 6){
                for(int i=0;i<50;i++) A[i] = 49-i;
            } else if(idx == 7){
                for(int i=0;i<50;i++) A[i] = 50-i;
            } else if(idx == 8){
                for(int i=0;i<50;i++) A[i] = -1000 + 25*i;
            } else if(idx == 9){
                for(int i=0;i<50;i++) A[i] = 1000 - 25*i;
            } else if(idx == 10){
                for(int i=0;i<50;i++) A[i] = (i%2==0?0:1000);
            } else if(idx == 11){
                for(int i=0;i<50;i++) A[i] = (i%2==0?0:-1000);
            } else if(idx == 12){
                for(int i=0;i<50;i++) A[i] = (i<25?0:1000);
            } else if(idx == 13){
                for(int i=0;i<50;i++) A[i] = (i<25?-1000:0);
            } else if(idx == 14){
                for(int i=0;i<50;i++) A[i] = primes[i];
            }
        }
        else if(t <= 35) {
            if(t <= 30) {
                N = 2;
                A.resize(2);
                if(t==27){ A = {1000,1000}; }
                if(t==28){ A = {1000,-1000}; }
                if(t==29){ A = {-1000,-1000}; }
                if(t==30){ A = {0,0}; }
            } else {
                N = 2;
                A.resize(2);
                if(t==31){ A = {0,1000}; }
                if(t==32){ A = {0,-1000}; }
                if(t==33){ A = {-1000,0}; }
                if(t==34){ A = {500,-500}; }
                if(t==35){ A = {123,-456}; }
            }
        }
        else {
            N = rand() % 50 + 1;
            A.resize(N);
            for(int i=0;i<N;i++){
                A[i] = rand() % 2001 - 1000;
            }
        }
        fout << N << "\n";
        for(int i=0;i<N;i++){
            fout << A[i] << (i+1<N?' ':'\n');
        }
        fout.close();
    }
    return 0;
}