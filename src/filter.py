from collections import Counter
from typing import Iterable, List

from src.constraints import Constraints


def filter_candidates(words: Iterable[str],
                      constraints: Constraints) -> List[str]:
    valid_words = []

    for word in words:
        # Greens
        if any(word[i] != c for i, c in constraints.green_positions.items()):
            continue

        wc = Counter(word)

        # Min counts
        if any(wc[c] < constraints.min_count[c]
               for c in constraints.min_count):
            continue

        # Max counts
        if any(wc[c] > constraints.max_count[c]
               for c in constraints.max_count):
            continue

        # Yellows
        violated = False
        for c, positions in constraints.yellow_positions.items():
            if c not in word:
                violated = True
                break
            if any(word[i] == c for i in positions):
                violated = True
                break

        if violated:
            continue

        valid_words.append(word)

    return valid_words
