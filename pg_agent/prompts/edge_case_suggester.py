# Prompt strings used by the Edge Case Suggester graph

PARSE_CONSTRAINTS_PROMPT = """Extract input constraints from the problem description below. Return them as a JSON array of objects.
Each object should include:
- name
- type (int, list[int], etc.)
- min or max if applicable
- extra properties like "sorted", "unique", etc.

Only include actual constraints, no explanations.
"""

EDGE_CASE_GENERATOR_PROMPT = """You're a test case generator. Given the following list of constraints, create up to 25 diverse and tricky test inputs.

Handle edge cases like:
- min, min-1, max, max+1
- empty list
- duplicates (if allowed or restricted)
- sorted vs unsorted (if sorted is specified)

Return a list of test cases in valid JSON.
"""

__all__ = [
    "PARSE_CONSTRAINTS_PROMPT",
    "EDGE_CASE_GENERATOR_PROMPT",
]
