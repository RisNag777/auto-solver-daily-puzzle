from collections import defaultdict

from puzzle_agent.game import get_feedback

import math


def partition_candidates(guess, candidates):
    """
    Input:
    guess - Str denoting the initial guess
    candidates - List denoting potential future guesses

    Output:
    partitions - Dict mapping feedback tuple to candidates
    """
    partitions = defaultdict(list)
    for solution in candidates:
        feedback = get_feedback(guess, solution)
        partitions[tuple(feedback)].append(solution)
    return partitions


def entropy_for_guess(guess, candidates):
    """
    Input:
    guess - Str denoting the initial guess
    candidates - List denoting potential future guesses

    Output:
    entropy - Float denoting the calculated entropy for a guess
    """
    partitions = partition_candidates(guess, candidates)
    total = len(candidates)
    entropy = 0.0
    for feedback, subset in partitions.items():
        p = len(subset) / total
        entropy -= p * math.log2(p)
    return entropy


def best_guess(possible_guesses, candidates):
    """
    Input:
    possible_guesses - List of all possible guesses
    candidates - List denoting potential future guesses

    Behavior:
    Finds and returns the guess with maximum entropy
    """
    scores = {}
    for guess in possible_guesses:
        scores[guess] = entropy_for_guess(guess, candidates)
    return max(scores, key=scores.get)
