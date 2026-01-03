from collections import Counter
from typing import Tuple

# 0 = gray
# 1 = yellow
# 2 = green
Feedback = Tuple[int, int, int, int, int]


def get_feedback(guess: str, solution: str) -> Feedback:
    """
    Compute Wordle-style feedback for a guess against the solution
    """
    feedback = [0] * 5
    solution_counts = Counter(solution)

    # Step 1: Mark greens
    for i in range(5):
        if guess[i] == solution[i]:
            feedback[i] = 2
            solution_counts[guess[i]] -= 1

    # Step 2: Mark yellows
    for i in range(5):
        if feedback[i] == 0 and solution_counts[guess[i]] > 0:
            feedback[i] = 1
            solution_counts[guess[i]] -= 1

    return tuple(feedback)
