import os
from dotenv import load_dotenv

load_dotenv()


def retrieve_word_list():
    data_folder = os.getenv("DATA_FOLDER", "data")
    words_path = f"{data_folder}/words.txt"

    with open(words_path, "r") as file:
        candidates = [line.rstrip("\n") for line in file]
        return candidates
