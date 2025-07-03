#include <bits/stdc++.h>
using namespace std;

int main() {
    // Seed the random number generator
    unsigned seed = std::chrono::high_resolution_clock::now().time_since_epoch().count();
    std::mt19937 gen(seed);
    
    // Create files for test cases
    int test_case_count = 20;
    
    for (int tc = 1; tc <= test_case_count; ++tc) {
        std::ofstream outfile(std::to_string(tc) + ".in");
        
        // Different types of test cases
        if (tc <= 5) {
            // Small test cases (n <= 10)
            int n = gen() % 5 + 3; // Array size between 3 and 7
            outfile << n << endl;
            
            vector<int> nums(n);
            for (int i = 0; i < n; ++i) {
                nums[i] = gen() % 20 - 10; // Small range (-10 to 9)
                outfile << nums[i] << " ";
            }
            outfile << endl;
            
            // Choose two random positions and make sure they sum to target
            int pos1 = gen() % n;
            int pos2;
            do {
                pos2 = gen() % n;
            } while (pos2 == pos1);
            
            int target = nums[pos1] + nums[pos2];
            outfile << target << endl;
        }
        else if (tc <= 10) {
            // Medium test cases (10 < n <= 100)
            int n = gen() % 41 + 10; // Array size between 10 and 50
            outfile << n << endl;
            
            vector<int> nums(n);
            for (int i = 0; i < n; ++i) {
                nums[i] = gen() % 200 - 100; // Medium range (-100 to 99)
                outfile << nums[i] << " ";
            }
            outfile << endl;
            
            // Choose two random positions and make sure they sum to target
            int pos1 = gen() % n;
            int pos2;
            do {
                pos2 = gen() % n;
            } while (pos2 == pos1);
            
            int target = nums[pos1] + nums[pos2];
            outfile << target << endl;
        }
        else if (tc <= 15) {
            // Large test cases (100 < n <= 1000)
            int n = gen() % 401 + 100; // Array size between 100 and 500
            outfile << n << endl;
            
            vector<int> nums(n);
            for (int i = 0; i < n; ++i) {
                nums[i] = gen() % 2000 - 1000; // Larger range (-1000 to 999)
                outfile << nums[i] << " ";
            }
            outfile << endl;
            
            // Choose two random positions and make sure they sum to target
            int pos1 = gen() % n;
            int pos2;
            do {
                pos2 = gen() % n;
            } while (pos2 == pos1);
            
            int target = nums[pos1] + nums[pos2];
            outfile << target << endl;
        }
        else {
            // Edge cases
            if (tc == 16) {
                // Minimum possible array size (2)
                outfile << "2" << endl;
                outfile << "-10 10" << endl;
                outfile << "0" << endl;
            }
            else if (tc == 17) {
                // Large array with all zeros except two elements
                int n = 100;
                outfile << n << endl;
                for (int i = 0; i < n; ++i) {
                    if (i == 25) outfile << "17 ";
                    else if (i == 75) outfile << "23 ";
                    else outfile << "0 ";
                }
                outfile << endl;
                outfile << "40" << endl;  // 17 + 23 = 40
            }
            else if (tc == 18) {
                // All identical numbers except one
                int n = 50;
                outfile << n << endl;
                for (int i = 0; i < n; ++i) {
                    if (i == 30) outfile << "15 ";
                    else outfile << "5 ";
                }
                outfile << endl;
                outfile << "20" << endl;  // 5 + 15 = 20
            }
            else if (tc == 19) {
                // Maximum and minimum values
                int n = 10;
                outfile << n << endl;
                outfile << "1000 -1000 500 -500 750 -750 250 -250 100 -100" << endl;
                outfile << "0" << endl;  // 1000 + (-1000) = 0
            }
            else if (tc == 20) {
                // Target that requires specific elements
                int n = 20;
                outfile << n << endl;
                for (int i = 0; i < n; ++i) {
                    outfile << (i * 5) << " ";
                }
                outfile << endl;
                outfile << "35" << endl;  // 15 + 20 = 35
            }
        }
        
        outfile.close();
    }
    
    return 0;
}