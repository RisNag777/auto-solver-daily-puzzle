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
