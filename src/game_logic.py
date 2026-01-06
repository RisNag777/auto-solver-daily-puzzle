from collections import Counter
from dotenv import load_dotenv

import os

load_dotenv()


def retrieve_word_list():
    data_folder = os.getenv("DATA_FOLDER", "data")
    words_path = f"{data_folder}/words.txt"

    with open(words_path, "r") as file:
        candidates = [line.rstrip("\n") for line in file]
        return candidates


def get_feedback(guess, solution):
    feedback = [0] * 5
    solution_counts = Counter(solution)

    for i in range(5):
        if guess[i] == solution[i]:
            feedback[i] = 2
            solution_counts[guess[i]] -= 1

    for i in range(5):
        if feedback[i] == 0 and solution_counts[guess[i]] > 0:
            feedback[i] = 1
            solution_counts[guess[i]] -= 1

    return feedback


def cow_bull_absent(guess, feedback):
    cows = {}
    bulls = {}
    absent = set()
    for f in range(len(feedback)):
        char = guess[f]
        if feedback[f] == 2:
            bulls[char] = f
        elif feedback[f] == 1:
            cows[char] = f
        else:
            absent.add(char)
    return cows, bulls, absent


def filter_candidates(candidates, filter_condition):
    """
    Generic function to filter a list of candidates based on a condition.

    Args:
        candidates: List of candidate words to filter
        filter_condition: Function that takes a candidate and returns True if
                          it should be kept.

    Returns:
        Filtered list of candidates
    """
    return [  # fmt: off
        candidate for candidate in candidates if filter_condition(candidate)
    ]


def trim_list(guess, feedback, candidates):
    cows, bulls, absent = cow_bull_absent(guess, feedback)

    # Filter by absent letters (letters not in the word at all)
    if absent:
        candidates = filter_candidates(
            candidates, lambda c: all(letter not in c for letter in absent)
        )

    # Filter by bulls (letters in the correct position)
    if bulls:
        candidates = filter_candidates(
            candidates,
            lambda c: all(  # fmt: off
                c[pos] == letter for letter, pos in bulls.items()
            ),
        )

    # Filter by cows (letters in the word but wrong position)
    if cows:
        candidates = filter_candidates(
            candidates,
            lambda c: all(
                letter in c and c[pos] != letter  # fmt: off
                for letter, pos in cows.items()
            ),
        )

    return candidates
