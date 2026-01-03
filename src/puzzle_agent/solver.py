from puzzle_agent.constraints import Constraints
from puzzle_agent.entropy import best_guess
from puzzle_agent.filter import filter_candidates
from puzzle_agent.game import get_feedback


class Solver:
    def __init__(self, all_candidates, all_possible_guesses):
        """
        Input:
        all_candidates - List containing the puzzle vocabulary
        all_possible_guesses - List containing all potential guesses
        """
        self.all_candidates = all_candidates.copy()
        self.all_possible_guesses = all_possible_guesses.copy()
        self.constraints = Constraints()
        self.guess_history = []

    def next_guess(self):
        """
        Behavior:
        Pick next guess based on current candidates and entropy
        """
        guess = best_guess(self.all_possible_guesses, self.all_candidates)
        return guess

    def apply_feedback(self, guess, feedback):
        """
        Input:
        guess - Str denoting the guess
        feedback - List containing the feedback for the guess

        Behavior:
        Apply feedback to update constraints and shrink candidate list
        """
        self.guess_history.append((guess, feedback))
        self.constraints.update(guess, feedback)
        self.all_candidates = filter_candidates(
            self.all_candidates, self.constraints  # fmt: skip
        )

    def solve(self, solution, max_turns=6):
        """
        Input:
        solution - Str denoting the final, secret solution
        max_turns - Int denoting the maximum guesses available to the user

        Output:
        Return a list of guesses
        """
        for turn in range(max_turns):
            guess = self.next_guess()
            fb = get_feedback(guess, solution)
            self.apply_feedback(guess, fb)
            print(
                f"Turn {turn + 1}: Guess = {guess}, Feedback = {fb}, "
                + f"Remaining candidates = {len(self.all_candidates)}"
            )
            if guess == solution:
                print(f"Solved in {turn + 1} turns!")
                return [g for g, _ in self.guess_history]

        print("Failed to solve within max turns")
        return [g for g, _ in self.guess_history]
