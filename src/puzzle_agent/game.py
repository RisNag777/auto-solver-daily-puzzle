from collections import Counter

# 0 = gray
# 1 = yellow
# 2 = green


def get_feedback(guess, solution):
    """
    Input:
    guess - Str denoting the first guess
    solution - Str denoting the solution of the puzzle

    Output:
    feedback - List denoting the feedback
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

    return feedback
