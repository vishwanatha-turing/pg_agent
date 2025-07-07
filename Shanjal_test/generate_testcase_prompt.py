# generate_testcase_prompt.py

GENERATE_TESTCASE_PROMPT = """You are an expert test case generator for competitive programming problems.
Given a problem statement, generate **55 to 60** diverse and challenging test cases that:

- Cover edge and corner cases
- Include minimum and maximum bounds
- Include randomized but valid inputs
- Stress test performance
- Obey all constraints strictly

Return each test case clearly on its own line.

Problem:
{problem_statement}
"""
