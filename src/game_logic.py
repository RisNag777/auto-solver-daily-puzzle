from collections import Counter
from dotenv import load_dotenv

import os
import random

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

    for letter in range(5):
        if guess[letter] == solution[letter]:
            feedback[letter] = 2
            solution_counts[guess[letter]] -= 1

    for letter in range(5):
        if feedback[letter] == 0 and solution_counts[guess[letter]] > 0:
            feedback[letter] = 1
            solution_counts[guess[letter]] -= 1

    return feedback


def cow_bull_absent(guess, feedback):
    cows = {}
    bulls = {}
    absent = set()
    for pos in range(len(feedback)):
        char = guess[pos]
        if feedback[pos] == 2:
            bulls[char] = pos
        elif feedback[pos] == 1:
            cows[char] = pos
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
            candidates,
            lambda candidate: all(  # fmt: off
                letter not in candidate for letter in absent
            ),
        )

    # Filter by bulls (letters in the correct position)
    if bulls:
        candidates = filter_candidates(
            candidates,
            lambda candidate: all(  # fmt: off
                candidate[pos] == letter for letter, pos in bulls.items()
            ),
        )

    # Filter by cows (letters in the word but wrong position)
    if cows:
        candidates = filter_candidates(
            candidates,
            lambda candidate: all(
                letter in candidate and candidate[pos] != letter  # fmt: off
                for letter, pos in cows.items()
            ),
        )

    return candidates


def random_word_select(candidates, num_words=20):
    random_word = []
    for _ in range(num_words):
        rng = random.randint(0, len(candidates))
        random_word.append(candidates[rng])
    return random_word
