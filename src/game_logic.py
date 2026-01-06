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


def trim_list(guess, feedback, candidates):
    cows, bulls, absent = cow_bull_absent(guess, feedback)
    if len(absent) == 0:
        abs_c = []
        for candidate in candidates:
            if all(letter not in candidate for letter in absent):
                abs_c.append(candidate)
    else:
        abs_c = candidates
    if bulls.keys() and not abs_c:
        bull_c = []
        for candidate in abs_c:
            if all(candidate[pos] == letter for letter, pos in bulls.items()):
                bull_c.append(candidate)
    else:
        bull_c = abs_c
    if cows.keys() and not bull_c:
        cow_c = []
        for candidate in bull_c:
            if all(
                letter in candidate and candidate[pos] != letter
                for letter, pos in cows.items()
            ):
                cow_c.append(candidate)
    else:
        cow_c = bull_c
    return cow_c
