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
    """
    Randomly select 1 or 2 topics from the curated list.
    Args:
        n (int): Number of topics to select (default 2, but can be 1).
    Returns:
        List[str]: List of selected topics.
    """
    n = max(1, min(n, 2))
    return random.sample(ALGORITHMIC_TOPICS, n)


if __name__ == "__main__":
    print("Selected topics:", select_topics())


def topic_selector_node(state):
    """
    Node that selects topics and adds them to the state.
    Uses the add reducer for topics list.
    """
    # Get topics using the existing function
    selected_topics = select_topics(n=2)

    # Return only the fields we're updating
    # Since topics uses the `add` reducer, it will handle the list update
    return {"topics": selected_topics}
