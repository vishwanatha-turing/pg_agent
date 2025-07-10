#include <bits/stdc++.h>
#include <future>
using namespace std;
using namespace chrono;  // Add this to fix milliseconds reference

// Global variable to signal thread interruption
atomic<bool> should_stop(false);

// Helper class to redirect stdin/stdout
class IORedirector {
    stringstream input, output;
    streambuf *old_cin, *old_cout;
public:
    IORedirector(const string& in) : input(in) {
        old_cin = cin.rdbuf(input.rdbuf());
        old_cout = cout.rdbuf(output.rdbuf());
    }
    
    ~IORedirector() {
        cin.rdbuf(old_cin);
        cout.rdbuf(old_cout);
    }
    
    string get_output() {
        return output.str();
    }
};

// Dummy brute force solution - replace with actual brute force logic
string solve_brute_force(const string& input_str) {
    // Simulate reading from stdin and writing to stdout
    IORedirector redirector(input_str);
    
    // This is where you put the actual brute force implementation
    // It can use cin/cout as normal
    int n;
    cin >> n;
    
    if (n == 42 || n == 87) {
        this_thread::sleep_for(seconds(11));  // Simulate slow work
    }
    
    cout << n << "\n";  // Write to simulated stdout
    return redirector.get_output();
}

// Dummy optimal solution - replace with actual optimal logic
string solve_optimal(const string& input_str) {
    // Simulate reading from stdin and writing to stdout
    IORedirector redirector(input_str);
    
    // This is where you put the actual optimal implementation
    // It can use cin/cout as normal
    int n;
    cin >> n;
    cout << n << "\n";
    
    return redirector.get_output();
}

// Function to find the next available test case number
int find_next_file_number() {
    int next_num = 1;
    while (true) {
        string filename = "test_cases/" + to_string(next_num) + ".in";
        ifstream file(filename);
        if (!file.good()) {
            return next_num;
        }
        next_num++;
    }
}

// Function to run a solution (either brute force or optimal) and write output
void run_solution(const string& input_file, const string& output_file, bool use_optimal, int test_num, int file_num) {
    cout << "Test " << setw(2) << test_num << " (files: " << setw(3) << file_num << ".in/out): ";
    cout.flush();
    
    // Read input file content
    ifstream fin(input_file);
    stringstream buffer;
    buffer << fin.rdbuf();
    string input_str = buffer.str();
    fin.close();
    
    // Solve using appropriate method
    string result;
    if (use_optimal) {
        result = solve_optimal(input_str);
        cout << "[optimal]" << endl;
    } else {
        // Try brute force with timeout
        auto future = async(launch::async, solve_brute_force, input_str);
        auto status = future.wait_for(seconds(10));
        
        if (status == future_status::timeout) {
            cout << "[timeout -> optimal]" << endl;
            result = solve_optimal(input_str);
        } else {
            result = future.get();
            cout << "[brute force]" << endl;
        }
    }
    
    // Write output
    ofstream fout(output_file);
    fout << result;
    fout.close();
}

// Function to generate a test case
void generate_test_case(int test_num, int file_num) {
    // Create input file
    string input_file = "test_cases/" + to_string(file_num) + ".in";
    ofstream fin(input_file);
    
    // Generate random test data
    int n = rand() % 100 + 1;
    fin << n << "\n";
    fin.close();
    
    // Generate output using brute force first, falling back to optimal if needed
    string output_file = "test_cases/" + to_string(file_num) + ".out";
    run_solution(input_file, output_file, false, test_num, file_num);
}

int main(int argc, char* argv[]) {
    srand(time(0));  // Initialize random seed
    
    // Create test_cases directory if it doesn't exist
    system("mkdir -p test_cases");
    
    int start_file_num = find_next_file_number();
    int num_tests = 50;
    
    cout << "Generating " << num_tests << " test cases starting from file number " << start_file_num << endl;
    cout << "--------------------------------------------------------------------------------" << endl;
    
    // Generate test cases
    for (int test_num = 1; test_num <= num_tests; test_num++) {
        int file_num = start_file_num + test_num - 1;
        generate_test_case(test_num, file_num);
    }
    
    cout << "--------------------------------------------------------------------------------" << endl;
    cout << "Test generation complete! Generated " << num_tests << " test cases." << endl;
    return 0;
}
