from collections import Counter


def filter_candidates(words, constraints):
    """
    Input:
    words - Str denoting the words to be guessed
    constraints - Updated constraints post the feedback from the first guess

    Output:
    valid_words - List with the validated words based on the constraints
    """
    valid_words = []

    for word in words:
        # Greens
        if any(word[i] != c for i, c in constraints.green_positions.items()):
            continue

        wc = Counter(word)

        # Min counts
        if any(  # fmt: skip
            wc[c] < constraints.min_count[c] for c in constraints.min_count
        ):
            continue

        # Max counts
        if any(  # fmt: skip
            wc[c] > constraints.max_count[c] for c in constraints.max_count
        ):
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
