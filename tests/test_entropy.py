from puzzle_agent.entropy import (  # fmt: skip
    best_guess,
    entropy_for_guess,
    partition_candidates,
)


def test_entropy_single_candidate():
    candidates = ["balmy"]
    guess = "balmy"
    ent = entropy_for_guess(guess, candidates)
    assert ent == 0.0, "Entropy for  single-candidate list should be 0"


def test_partition_candidates_correctness():
    candidates = ["balmy", "bally"]
    guess = "alley"
    partitions = partition_candidates(guess, candidates)

    # Each candidate should appear in exactly one partition
    all_partitioned = sum(len(v) for v in partitions.values())
    assert all_partitioned == len(candidates)

    # Partition keys should be tuples of length 5
    for fb in partitions:
        assert isinstance(fb, tuple)
        assert len(fb) == 5


def test_best_guesses_basic():
    candidates = ["bally", "balmy"]
    possible_guesses = ["balmy", "bally", "alley"]
    guess = best_guess(possible_guesses, candidates)
    assert guess in possible_guesses, "Best guess must be one of the possible guesses"
