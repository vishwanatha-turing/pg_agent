from sum_of_array import findPairs

def test_case_1():
    assert findPairs([3, 1, 4, 1, 5], 2) == 2

def test_case_2():
    assert findPairs([1, 2, 3, 4, 5], 1) == 4

def test_case_3():
    assert findPairs([1, 3, 1, 5, 4], 0) == 1

def test_case_4():
    assert findPairs([1, 2, 3, 4, 5], 0) == 0

def test_case_5():
    assert findPairs([1, 1, 1, 2, 2], 0) == 2	