#include <bits/stdc++.h>

int main() {
    // Seed the random number generator
    unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
    std::mt19937 gen(seed);
    
    // Create 15 test cases
    for (int tc = 1; tc <= 15; ++tc) {
        std::ofstream outfile(std::to_string(tc) + ".in");
        
        int n;
        std::vector<int> nums;
        int target;
        
        // Different distributions for different test cases
        if (tc <= 3) {
            // Small test cases (2-10 elements)
            n = std::uniform_int_distribution<int>(2, 10)(gen);
            std::uniform_int_distribution<int> val_dist(-20, 20);
            
            for (int i = 0; i < n; ++i) {
                nums.push_back(val_dist(gen));
            }
            
            // Ensure at least one valid solution exists
            int idx1 = std::uniform_int_distribution<int>(0, n-2)(gen);
            int idx2 = std::uniform_int_distribution<int>(idx1+1, n-1)(gen);
            target = nums[idx1] + nums[idx2];
            
        } else if (tc <= 6) {
            // Medium test cases (11-100 elements)
            n = std::uniform_int_distribution<int>(11, 100)(gen);
            std::uniform_int_distribution<int> val_dist(-100, 100);
            
            for (int i = 0; i < n; ++i) {
                nums.push_back(val_dist(gen));
            }
            
            // Ensure at least one valid solution exists
            int idx1 = std::uniform_int_distribution<int>(0, n-2)(gen);
            int idx2 = std::uniform_int_distribution<int>(idx1+1, n-1)(gen);
            target = nums[idx1] + nums[idx2];
            
        } else if (tc <= 9) {
            // Large test cases (101-1000 elements)
            n = std::uniform_int_distribution<int>(101, 1000)(gen);
            std::uniform_int_distribution<int> val_dist(-1000, 1000);
            
            for (int i = 0; i < n; ++i) {
                nums.push_back(val_dist(gen));
            }
            
            // Ensure at least one valid solution exists
            int idx1 = std::uniform_int_distribution<int>(0, n-2)(gen);
            int idx2 = std::uniform_int_distribution<int>(idx1+1, n-1)(gen);
            target = nums[idx1] + nums[idx2];
            
        } else if (tc == 10) {
            // Edge case: only 2 elements
            n = 2;
            nums = {5, 10};
            target = 15;
            
        } else if (tc == 11) {
            // Edge case: duplicate numbers
            n = 5;
            nums = {3, 3, 3, 3, 3};
            target = 6;
            
        } else if (tc == 12) {
            // Edge case: target = 0 with negative numbers
            n = 6;
            nums = {-2, -1, 0, 1, 2, 3};
            target = 0;
            
        } else if (tc == 13) {
            // Edge case: all negative numbers
            n = 5;
            nums = {-5, -4, -3, -2, -1};
            target = -7;
            
        } else if (tc == 14) {
            // Edge case: all zeros
            n = 5;
            nums = {0, 0, 0, 0, 0};
            target = 0;
            
        } else if (tc == 15) {
            // Edge case: max range
            n = 10;
            std::uniform_int_distribution<int> val_dist(-10000, 10000);
            
            for (int i = 0; i < n; ++i) {
                nums.push_back(val_dist(gen));
            }
            
            int idx1 = std::uniform_int_distribution<int>(0, n-2)(gen);
            int idx2 = std::uniform_int_distribution<int>(idx1+1, n-1)(gen);
            target = nums[idx1] + nums[idx2];
        }
        
        // Write to file
        outfile << n << std::endl;
        for (int i = 0; i < n; ++i) {
            outfile << nums[i];
            if (i < n-1) outfile << " ";
        }
        outfile << std::endl;
        outfile << target << std::endl;
        
        outfile.close();
    }
    
    return 0;
}