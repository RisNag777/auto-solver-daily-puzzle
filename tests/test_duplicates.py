from src.constraints import Constraints
from src.filter import filter_candidates
from src.game import get_feedback


def test_alley_balmy_case():
    guess = "alley"
    solution = "balmy"

    feedback = get_feedback(guess, solution)

    c = Constraints()
    c.update(guess, feedback)

    words = ["balmy", "sally", "alley", "bally"]
    valid = filter_candidates(words, c)

    assert "balmy" in valid
    assert "bally" in valid
    assert "sally" not in valid  # too many 'l's
    assert "alley" not in valid  # 'a' in wrong position
