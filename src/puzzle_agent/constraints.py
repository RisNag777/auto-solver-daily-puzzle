from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, Set, Tuple


@dataclass
class Constraints:
    green_positions: Dict[int, str] = field(default_factory=dict)
    yellow_positions: Dict[str, Set[int]] = field(
        default_factory=lambda: defaultdict(set)
    )
    min_count: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    max_count: Dict[str, int] = field(default_factory=lambda: defaultdict(
        lambda: 5))

    def update(self, guess: str,
               feedback: Tuple[int, int, int, int, int]) -> None:
        """
        Update constraints given a guess and feedback
        """
        guess_counts = Counter(guess)
        non_gray_counts = Counter(
                guess[i] for i in range(5) if feedback[i] > 0)

        # Greens & Yellows, positional
        for i, (letter, fb) in enumerate(zip(guess, feedback)):
            if fb == 2:
                self.green_positions[i] = letter
            elif fb == 1:
                self.yellow_positions[letter].add(i)
            elif fb == 0:
                # Only restrict positions if this letter occurs elsewhere as non-gray
                if guess_counts[letter] > non_gray_counts.get(letter, 0):
                    # Letter occurs in guess more times than in non-gray feedback
                    self.max_count[letter] = min(self.max_count[letter], non_gray_counts.get(letter, 0))

        # Min counts
        for letter, count in non_gray_counts.items():
            self.min_count[letter] = max(self.min_count[letter], count)

        # Max counts
        for letter in guess_counts:
            if letter in non_gray_counts:
                if guess_counts[letter] > non_gray_counts[letter]:
                    self.max_count[letter] = min(
                        self.max_count[letter], non_gray_counts[letter]
                    )
            else:
                # Fully gray letter
                self.max_count[letter] = 0
