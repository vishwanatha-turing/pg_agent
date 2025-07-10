#include <bits/stdc++.h>
using namespace std;

int main() {
    srand(time(0));
    int t = 50 + rand() % 51; // generates between 50 and 100 test cases
    ofstream outfile;

    for (int i = 1; i <= t; ++i) {
        outfile.open(to_string(i) + ".in");
        int x = rand() % 100 + 1;
        int y = rand() % 100 + 1;
        int k = rand() % 10 + 1;

        // Create specific cases
        if (i % 10 == 0) {
            // case where x = y
            y = x;
        }
        else if (i % 10 == 1) {
            // case where x is much greater than y
            y = rand() % (x / 2) + 1;
        }
        else if (i % 10 == 2) {
            // case where y is much greater than x
            x = rand() % (y / 2) + 1;
        }
        else if (i % 10 == 3) {
            // case with maximum k
            k = 10;
        }
        else if (i % 10 == 4) {
            // case including negatives
            x = rand() % 50 - 25; // from -25 to 24
            y = rand() % 50 - 25; // from -25 to 24
            // ensure we have valid positive k
            k = rand() % 10 + 1;
        }
        else if (i % 10 == 5) {
            // case with duplicates
            x = rand() % 50 + 1;
            y = x;
            k = rand() % 10 + 1;
        }
        else if (i % 10 == 6) {
            // case where x = 1
            x = 1;
            k = rand() % 10 + 1;
            if (rand() % 2) {
                y = 1 + rand() % 50;
            } else {
                y = 1;
            }
        }
        else if (i % 10 == 7) {
            // case where k = 1, only multiplying by 1
            k = 1;
            y = 1 + rand() % 50;
        }
        else if (i % 10 == 8) {
            // case with large x and y, but small k
            x = rand() % 100 + 900000;
            y = x + (rand() % 1000);
            k = 3; // small k
        }
        else {
            // case with various small ranges
            x = rand() % 50 + 1;
            y = rand() % 50 + 1;
            k = rand() % 10 + 1;
        }

        outfile << x << " " << y << " " << k << "\n";
        outfile.close();
    }
    return 0;
}