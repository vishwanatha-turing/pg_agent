problem_spec = {
    "title": "Hard Original Problem Prompt Specification",
    "metadata": {
        "difficulty": "Div. 1 / ICPC-level",
        "time_limit_seconds": 2,
        "memory_limit_mb": 256,
        "constraints_level": "High",
        "input_size": "n ≥ 1e5",
        "expected_time_complexity": "O(n log n) or better",
    },
    "requirements": {
        "novelty": {
            "description": "The problem must not resemble well-known problems (e.g., Dijkstra, knapsack, segment tree variants).",
            "Requirement": "Strictly Requires fresh insight or reduction from advanced or obscure topics like computational geometry, randomized algorithms, or deep graph theory.",
        },
        "layered_difficulty": {
            "description": "The solution approach must unfold in distinct layers of insight.",
            "layers": {
                "layer_1": "Naive brute-force or greedy solution that intuitively seems plausible but fails due to constraints.",
                "layer_2": "Well-known DS/Algo that performs better (e.g., prefix sums, binary search, line sweep) but fails due to subtle edge cases or structural limitations.",
                "layer_3": "Final correct solution combines 2 or more advanced techniques or insights (e.g., Mo’s Algorithm + fractional cascading, or DP with persistent segment trees)."
            }
        },
        "deceptive_simplicity": {
            "description": "The problem statement must be short and sound approachable to lure competitors into trying naive strategies.",
            "requirement": "True complexity should be embedded in the definition of ‘valid’, ‘optimal’, or ‘consistent’ — with constraints or definitions that create complexity behind the scenes."
        },
        "anti_pattern": {
            "description": "Do not use typical problem formats or phrasing (e.g., 'given a tree', 'find the shortest path', 'answer q queries').",
            "requirement": "Use unconventional or implicit structures (e.g., implicit hypergraphs, overlapping dynamic intervals, or interdependent sliding windows)."
        },
        "input_output_spec": {
            "description": "Design edge cases and corner cases intentionally.",
            "edge_cases": [
                "Adversarial inputs designed to break O(n^2) or even some O(n log n) heuristics",
                "Floating-point edge cases (e.g., precision errors due to accumulation)",
                "Boundary cases (e.g., n=1, n=1e5, all values equal, strictly increasing/decreasing patterns)",
                "Repeated elements with hidden structural properties"
            ]
        },
        "sample_explanation": {
            "description": "The sample input and output must not be easily traceable by hand to reveal the trick or main insight.",
            "requirement": "Even experienced contestants should need to simulate multiple paths or steps to manually deduce the output."
        },
        "hidden_trap": {
            "description": "Include a constraint or rule that subtly invalidates common greedy/heuristic approaches.",
            "examples": [
                "Parity constraints (e.g., certain conditions only hold when a sum is even)",
                "Modular wrap-around behavior in constraints (e.g., arithmetic modulo a prime number)",
                "Edge label dependencies or inter-variable hidden constraints"
            ]
        }
    },
    "output_format": {
        "description": "Clearly define what the output must represent.",
        "constraints": [
            "Must handle large outputs if required (e.g., multiple answers or bitmasks)",
            "Ensure the output format rules allow for multiple valid outputs (where applicable)"
        ]
    },
    "evaluation_criteria": {
        "scoring": "Binary (correct/incorrect), with hidden edge cases to detect non-rigorous implementations.",
        "failure_cases": "Naive, greedy, or singly-optimized approaches must TLE, WA, or fail on precision errors."
    },
    "misc_notes": {
        "applicability": "Can be used in ICPC regionals, Codeforces Div. 1, or IOI finals",
        "reusability": "Encourage tweaking structure or constraints to generate multiple problem variants",
        "discouraged_topics": [
            "Direct sorting + prefix sums",
            "Heavy use of STL containers solving the problem trivially",
            "Explicit query-based problems unless the queries interact in non-trivial ways"
        ]
    }
}
