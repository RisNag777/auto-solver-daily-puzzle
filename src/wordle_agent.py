from collections import defaultdict


def feedback_explanation(turn, guess, feedback):
    """
    Generate a human-readable explanation of feedback from a Wordle guess.

    Creates a formatted string that explains the current game state and
    categorizes each letter in the guess based on the feedback:
    - Absent (0): Letters not in the solution
    - Cows (1): Letters in the solution but wrong position
    - Bulls (2): Letters in the correct position

    Args:
        turn (int): The current turn number (out of 6).
        guess (str): The 5-letter word that was guessed.
        feedback (list[int]): List of feedback values (0, 1, or 2) for each
                              position, typically from get_feedback().

    Returns:
        str: A formatted string explaining the turn, guess, feedback, and
             categorization of each letter with its position information.

    Example:
        >>> feedback_explanation(1, "CRANE", [0, 0, 2, 2, 2])
        "It is currently turn 1 out of 6.\\nThe guessed word is CRANE.\\n..."
    """
    fb_exp = f"""It is currently turn {turn} out of 6.\nThe guessed word is
    {guess}.\nThe feedback is {feedback}\n\n"""
    absent, bulls, cows = [], defaultdict(list), defaultdict(list)
    for i in range(5):
        if feedback[i] == 0:
            absent.append(guess[i])
        if feedback[i] == 1:
            cows[guess[i]].append(i)
        if feedback[i] == 2:
            bulls[guess[i]].append(i)

    fb_exp += f"""- The letters {', '.join(absent)} are not in the
    solution (0).\n"""
    for char, pos in bulls.items():
        fb_exp += f"""- The letter {char} is in the correct position (2) at
        index {pos}.\n"""
    for char, pos in cows.items():
        fb_exp += f"""- The letter {char} is in the solution but not in the
        correct position (1). Anywhere other than index {pos}.\n"""
    return fb_exp
