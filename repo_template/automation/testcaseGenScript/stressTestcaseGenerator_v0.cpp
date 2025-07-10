#include <bits/stdc++.h>
using namespace std;

void generateMediumSizedRandomCases(int n) {
    ofstream out("medium_random_cases.txt");
    out << n << "\n";
    for (int i = 0; i < n; i++) {
        int x = rand() % (1000000 - 1 + 1) + 1;
        int y = rand() % (1000000 - 1 + 1) + 1;
        int k = rand() % (1000000 - 1 + 1) + 1;
        out << x << " " << y << " " << k << "\n";
    }
    out.close();
}

void generateLargeSizedRandomCases(int n) {
    ofstream out("large_random_cases.txt");
    out << n << "\n";
    for (int i = 0; i < n; i++) {
        int x = rand() % 1000000 + 1;
        int y = rand() % 1000000 + 1;
        int k = 1000000; // Use maximum constraint for k
        out << x << " " << y << " " << k << "\n";
    }
    out.close();
}

void generateEdgeCases(int n) {
    ofstream out("edge_cases.txt");
    out << n << "\n";
    out << "1 1 1\n"; // Simple case
    out << "1 1000000 1\n"; // Maximum y
    out << "1000000 1 1\n"; // Maximum x
    out << "1000000 1000000 1\n"; // Both maximum
    out << "1 1 1000000\n"; // Maximum k
    out.close();
}

void generatePatternBasedCases() {
    ofstream out("pattern_based_cases.txt");
    out << 3 << "\n";
    out << "1000000 1000000 1000000\n"; // All max
    out << "2 4 2\n"; // Simple doubling
    out << "3 9 3\n"; // Power case
    out.close();
}

int main() {
    srand(time(0));
    generateMediumSizedRandomCases(5);
    generateLargeSizedRandomCases(5);
    generateEdgeCases(5);
    generatePatternBasedCases();
    return 0;
}