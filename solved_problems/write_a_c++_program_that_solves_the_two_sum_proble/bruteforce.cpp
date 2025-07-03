#include <iostream>
#include <vector>

std::vector<int> twoSum(std::vector<int>& nums, int target) {
    std::vector<int> result;
    for (int i = 0; i < nums.size(); i++) {
        for (int j = i + 1; j < nums.size(); j++) {
            if (nums[i] + nums[j] == target) {
                result.push_back(i);
                result.push_back(j);
                return result;
            }
        }
    }
    return result;
}

int main() {
    int n;
    std::cin >> n;
    
    std::vector<int> nums(n);
    for (int i = 0; i < n; i++) {
        std::cin >> nums[i];
    }
    
    int target;
    std::cin >> target;
    
    std::vector<int> result = twoSum(nums, target);
    
    std::cout << result[0] << " " << result[1] << std::endl;
    
    return 0;
}