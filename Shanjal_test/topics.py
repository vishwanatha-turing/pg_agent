import random
from typing import List

# Curated list of algorithmic topics
ALGORITHMIC_TOPICS = [
    "Dynamic Programming",
    "Graphs",
    "Greedy Algorithms",
    "Number Theory",
    "Combinatorics",
    "Geometry",
    "Data Structures",
    "Strings",
    "Math",
    "Bit Manipulation",
    "Game Theory",
    "Probability",
    "Network Flow",
    "Divide and Conquer",
    "Recursion",
    "Trees",
    "Hashing",
    "Sorting and Searching",
    "Constructive Algorithms",
    "Disjoint Set Union (DSU)",
    "Segment Trees",
    "Fenwick Trees (BIT)",
    "Trie",
    "Suffix Structures",
    "Heavy-Light Decomposition",
    "Binary Search",
    "Backtracking",
    "Meet in the Middle",
    "Randomized Algorithms",
    "2-SAT",
    "FFT/NTT",
    "Matrix Exponentiation",
    "Persistent Data Structures",
    "Mo's Algorithm",
    "Centroid Decomposition",
    "Euler Tour Techniques",
    "Bitmask DP",
    "Interactive Problems",
]


def select_topics(n: int = 2) -> List[str]:
    """Randomly select *n* topics from the curated list (1 ≤ n ≤ 2)."""
    n = max(1, min(n, 2))
    return random.sample(ALGORITHMIC_TOPICS, n)


def topic_selector_node(state):
    """LangGraph node: selects topics and adds them to the state (uses *add* reducer)."""
    selected_topics = select_topics(n=2)
    return {"topics": selected_topics}


# ---------------------------------------------------------------------------
# CLI helper for a quick manual test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Selected topics:", select_topics())
