from collections import Counter
from dotenv import load_dotenv

import os
import random

load_dotenv()


def retrieve_word_list():
    """
    Retrieve a list of words from the words.txt file.

    Reads words from a text file located in the data folder.
    The function reads from words.txt within that folder.

    Returns:
        list[str]: A list of words, with newline characters stripped from
                   each word.

    Raises:
        FileNotFoundError: If the words.txt file cannot be found in the
                          specified data folder.
    """
    data_folder = os.getenv("DATA_FOLDER", "data")
    words_path = f"{data_folder}/words.txt"

    with open(words_path, "r") as file:
        candidates = [line.rstrip("\n") for line in file]
        return candidates


def get_feedback(guess_list, solution_list):
    """
    Compute Wordle-style feedback for a guess against the solution.

    For each character in the guess, returns:
      - 2 if the letter is in the correct position (bull)
      - 1 if the letter is in the solution but in a different position (cow)
      - 0 if the letter is not in the solution (absent)

    The function processes bulls first to ensure exact matches are prioritized,
    then assigns cows without double-counting any letter in the solution.

    Args:
        guess_list (list[str]): List of characters from the guessed word.
        solution_list (list[str]): List of characters from the solution word.

    Returns:
        list[int]: Feedback list of length 5, each value being 0, 1, or 2.

    Example:
        >>> get_feedback(list("CRANE"), list("CRANE"))
        [2, 2, 2, 2, 2]
        >>> get_feedback(list("CRANE"), list("PLANE"))
        [0, 0, 2, 2, 2]
        >>> get_feedback(list("CRANE"), list("REACT"))
        [1, 1, 2, 0, 1]
    """
    feedback = [0] * 5
    solution_counts = Counter(solution_list)

    for letter in range(5):
        if guess_list[letter] == solution_list[letter]:
            feedback[letter] = 2
            solution_counts[guess_list[letter]] -= 1

    for letter in range(5):
        if feedback[letter] == 0 and solution_counts[guess_list[letter]] > 0:
            feedback[letter] = 1
            solution_counts[guess_list[letter]] -= 1

    return feedback


def cow_bull_absent(guess, feedback):
    """
    Categorize letters from a guess based on feedback into
    bulls, cows, and absent.

    Analyzes the feedback for each position in the guess and categorizes
    letters:
    - Bulls: Letters in the correct position (feedback value 2)
    - Cows: Letters in the word but wrong position (feedback value 1)
    - Absent: Letters not in the word (feedback value 0)

    Args:
        guess (str): The word that was guessed.
        feedback (list[int]): List of feedback values (0, 1, or 2) for each
                              position, typically from get_feedback().

    Returns:
        tuple[dict[str, int], dict[str, int], set[str]]: A tuple containing:
            - cows: Dictionary mapping letters to their position in the guess
                    where they appear but are in the wrong position.
            - bulls: Dictionary mapping letters to their position in the guess
                     where they are in the correct position.
            - absent: Set of letters that are not in the solution word.

    Example:
        >>> guess = "CRANE"
        >>> feedback = [1, 1, 2, 0, 1]
        >>> cows, bulls, absent = cow_bull_absent(guess, feedback)
        >>> bulls
        {'R': 2}
        >>> cows
        {'C': 0, 'A': 1, 'E': 4}
        >>> absent
        {'N'}
    """
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
            if char in bulls or char in cows:
                continue
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
    """
    Filter candidate words based on feedback from a guess.

    Takes a guess, its feedback, and a list of candidate words, then filters
    the candidates to only include words that are consistent with the feedback.
    The filtering is done in three stages:
    1. Remove words containing absent letters (letters not in solution)
    2. Keep only words with letters in correct positions
    3. Keep only words with letters present but in different positions

    Args:
        guess (str): The word that was guessed.
        feedback (list[int]): List of feedback values (0, 1, or 2) for each
                              position, typically from get_feedback().
        candidates (list[str]): List of candidate words to filter.

    Returns:
        list[str]: Filtered list of candidate words that are consistent with
                   the feedback from the guess.

    Example:
        >>> candidates = ["CRANE", "PLANE", "CRATE", "SLATE"]
        >>> feedback = [0, 0, 2, 2, 2]  # "CRANE" vs "PLANE"
        >>> trim_list("CRANE", feedback, candidates)
        ['PLANE']
    """
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
    """
    Select a specified number of random words from a list of candidates.

    Randomly selects words from the candidates list, allowing duplicates.
    The selection is done with replacement, meaning the same word can be
    selected multiple times.

    Args:
        candidates (list[str]): List of candidate words to select from.
        num_words (int, optional): Number of random words to select.
                                   Defaults to 20.

    Returns:
        list[str]: List of randomly selected words from the candidates.

    Example:
        >>> candidates = ["CRANE", "PLANE", "CRATE", "SLATE"]
        >>> random_word_select(candidates, num_words=3)
        ['PLANE', 'CRANE', 'PLANE']
    """
    random_word = []
    for _ in range(num_words):
        rng = random.randint(0, len(candidates) - 1)
        random_word.append(candidates[rng])
    return random_word
