#include <bits/stdc++.h>
using namespace std;

int main()
{
    srand(time(0));

    int numberOfFiles = 5; // 🔢 Number of input files
    int maxTestCases = 20; // 🧪 Up to 20 test cases per file
    int maxVal = 50;       // 📏 Limit x, y, k <= 50 for small test cases

    for (int fileNum = 1; fileNum <= numberOfFiles; ++fileNum)
    {
        string fname = to_string(fileNum) + ".in";
        ofstream fout(fname);

        int t = rand() % maxTestCases + 1;
        fout << t << "\n";

        for (int i = 0; i < t; ++i)
        {
            int x = rand() % maxVal + 1;
            int y = rand() % maxVal + 1;
            int k = rand() % maxVal + 1;
            fout << x << " " << y << " " << k << "\n";
        }

        fout.close();
        cout << "✅ Generated: " << fname << "\n";
    }

    return 0;
}
