"""Unit tests for game_logic module."""

import os
import tempfile
from unittest.mock import patch

import pytest

from src.game_logic import (
    retrieve_word_list,
    get_feedback,
    cow_bull_absent,
    filter_candidates,
    trim_list,
    random_word_select,
)


class TestRetrieveWordList:
    """Tests for retrieve_word_list function."""

    def test_retrieve_word_list_default_path(self):
        """Test retrieving word list with default data folder."""
        words = retrieve_word_list()
        assert isinstance(words, list)
        assert len(words) > 0
        assert all(isinstance(word, str) for word in words)
        assert all(len(word) > 0 for word in words)

    @patch.dict(os.environ, {"DATA_FOLDER": "data"})
    def test_retrieve_word_list_with_env_var(self):
        """Test retrieving word list with DATA_FOLDER environment variable."""
        words = retrieve_word_list()
        assert isinstance(words, list)
        assert len(words) > 0

    def test_retrieve_word_list_file_not_found(self):
        """Test that FileNotFoundError is raised when file doesn't exist."""
        with patch.dict(os.environ, {"DATA_FOLDER": "nonexistent"}):
            with pytest.raises(FileNotFoundError):
                retrieve_word_list()

    def test_retrieve_word_list_strips_newlines(self):
        """Test that newlines are stripped from words."""
        test_content = "word1\nword2\nword3\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "words.txt")
            with open(test_file, "w") as f:
                f.write(test_content)
            with patch.dict(os.environ, {"DATA_FOLDER": tmpdir}):
                words = retrieve_word_list()
                assert words == ["word1", "word2", "word3"]
                assert all("\n" not in word for word in words)


class TestGetFeedback:
    """Tests for get_feedback function."""

    def test_perfect_match(self):
        """Test feedback for perfect match."""
        feedback = get_feedback("CRANE", "CRANE")
        assert feedback == [2, 2, 2, 2, 2]

    def test_no_match(self):
        """Test feedback when no letters match."""
        feedback = get_feedback("ABCDE", "FGHIJ")
        assert feedback == [0, 0, 0, 0, 0]

    def test_partial_match_correct_positions(self):
        """Test feedback with some letters in correct positions."""
        feedback = get_feedback("CRANE", "PLANE")
        assert feedback == [0, 0, 2, 2, 2]

    def test_letters_in_wrong_position(self):
        """Test feedback with letters in word but wrong position."""
        feedback = get_feedback("CRANE", "REACT")
        assert feedback == [1, 1, 2, 0, 1]

    def test_duplicate_letters_in_guess(self):
        """Test feedback with duplicate letters in guess."""
        # "E" appears twice in guess, but only once in solution
        feedback = get_feedback("EERIE", "CRANE")
        # E at position 0: absent (0), E at position 1: absent (0),
        # R at position 2: cow (1), I at position 3: absent (0),
        # E at position 4: bull (2) - matches solution
        assert feedback == [0, 0, 1, 0, 2]

    def test_duplicate_letters_in_solution(self):
        """Test feedback with duplicate letters in solution."""
        # Solution has two L's, guess has one
        feedback = get_feedback("PLANE", "LLAMA")
        # P: absent (0), L at position 1: bull (2), A at position 2: bull (2),
        # N: absent (0), E: absent (0)
        assert feedback == [0, 2, 2, 0, 0]

    def test_all_cows(self):
        """Test feedback when all letters are in word but wrong positions."""
        feedback = get_feedback("CRANE", "NECAR")
        assert all(f == 1 for f in feedback)

    def test_mixed_feedback(self):
        """Test feedback with mix of bulls, cows, and absent."""
        feedback = get_feedback("STARE", "CRATE")
        # S: absent (0), T: cow (1), A: bull (2), R: cow (1), E: bull (2)
        assert feedback == [0, 1, 2, 1, 2]


class TestCowBullAbsent:
    """Tests for cow_bull_absent function."""

    def test_all_bulls(self):
        """Test categorization when all letters are bulls."""
        guess = "CRANE"
        feedback = [2, 2, 2, 2, 2]
        cows, bulls, absent, excluded = cow_bull_absent(guess, feedback)
        assert bulls == {"C": [0], "R": [1], "A": [2], "N": [3], "E": [4]}
        assert cows == {}
        assert absent == set()
        assert excluded == []

    def test_all_absent(self):
        """Test categorization when all letters are absent."""
        guess = "ABCDE"
        feedback = [0, 0, 0, 0, 0]
        cows, bulls, absent, excluded = cow_bull_absent(guess, feedback)
        assert bulls == {}
        assert cows == {}
        assert absent == {"A", "B", "C", "D", "E"}
        assert excluded == []

    def test_all_cows(self):
        """Test categorization when all letters are cows."""
        guess = "CRANE"
        feedback = [1, 1, 1, 1, 1]
        cows, bulls, absent, excluded = cow_bull_absent(guess, feedback)
        assert bulls == {}
        assert cows == {"C": [0], "R": [1], "A": [2], "N": [3], "E": [4]}
        assert absent == set()
        assert excluded == []

    def test_mixed_categorization(self):
        """Test categorization with mix of bulls, cows, and absent."""
        guess = "CRANE"
        feedback = [1, 1, 2, 0, 1]
        cows, bulls, absent, excluded = cow_bull_absent(guess, feedback)
        assert bulls == {"A": [2]}
        assert cows == {"C": [0], "R": [1], "E": [4]}
        assert absent == {"N"}
        assert excluded == []

    def test_duplicate_letters(self):
        """Test categorization with duplicate letters."""
        guess = "EERIE"
        feedback = [1, 0, 1, 0, 1]
        cows, bulls, absent, excluded = cow_bull_absent(guess, feedback)
        assert "E" in cows
        assert "I" in absent
        assert "R" in cows
        # E at positions 1 and 3 got 0 but E is in word -> excluded_positions
        assert ("E", 1) in excluded
        assert ("E", 3) in excluded

    def test_duplicate_letter_bull_and_zero(self):
        """Test banns vs pawns: n at pos 2 gets 0, n at pos 3 gets 2."""
        guess = "banns"
        feedback = [0, 2, 0, 2, 2]
        cows, bulls, absent, excluded = cow_bull_absent(guess, feedback)
        assert bulls == {"a": [1], "n": [3], "s": [4]}
        assert absent == {"b"}
        assert ("n", 2) in excluded


class TestFilterCandidates:
    """Tests for filter_candidates function."""

    def test_filter_by_length(self):
        """Test filtering candidates by length."""
        candidates = ["CAT", "DOG", "ELEPHANT", "BIRD"]
        result = filter_candidates(candidates, lambda c: len(c) == 3)
        assert result == ["CAT", "DOG"]

    def test_filter_by_starting_letter(self):
        """Test filtering candidates by starting letter."""
        candidates = ["CAT", "DOG", "CUP", "BIRD"]
        result = filter_candidates(candidates, lambda c: c.startswith("C"))
        assert result == ["CAT", "CUP"]

    def test_filter_all_pass(self):
        """Test filtering when all candidates pass."""
        candidates = ["CAT", "DOG", "BIRD"]
        result = filter_candidates(candidates, lambda c: True)
        assert result == candidates

    def test_filter_none_pass(self):
        """Test filtering when no candidates pass."""
        candidates = ["CAT", "DOG", "BIRD"]
        result = filter_candidates(candidates, lambda c: False)
        assert result == []

    def test_filter_empty_list(self):
        """Test filtering empty candidate list."""
        candidates = []
        result = filter_candidates(candidates, lambda c: len(c) > 0)
        assert result == []


class TestTrimList:
    """Tests for trim_list function."""

    def test_trim_with_perfect_match_feedback(self):
        """Test trimming with perfect match feedback."""
        candidates = ["CRANE", "PLANE", "CRATE", "SLATE"]
        feedback = [2, 2, 2, 2, 2]  # Perfect match
        result = trim_list("CRANE", feedback, candidates)
        assert result == ["CRANE"]

    def test_trim_with_absent_letters(self):
        """Test trimming removes words with absent letters."""
        candidates = ["CRANE", "PLANE", "CRATE", "SLATE"]
        feedback = [0, 0, 2, 2, 2]  # C and R absent, A, N, E correct
        result = trim_list("CRANE", feedback, candidates)
        # Should only keep words with A, N, E in positions 2, 3, 4
        # and without C or R
        assert "CRANE" not in result  # Has C and R
        assert "CRATE" not in result  # Has C and R
        assert "PLANE" in result  # Has A, N, E in correct positions, no C or R

    def test_trim_with_bulls(self):
        """Test trimming with bulls (correct positions)."""
        candidates = ["CRANE", "PLANE", "CRATE", "SLATE"]
        feedback = [0, 0, 2, 2, 2]  # Positions 2, 3, 4 must be A, N, E
        result = trim_list("CRANE", feedback, candidates)
        for word in result:
            assert word[2] == "A"
            assert word[3] == "N"
            assert word[4] == "E"

    def test_trim_with_cows(self):
        """Test trimming with cows (wrong positions)."""
        candidates = ["CRANE", "PLANE", "CRATE", "SLATE", "REACT"]
        feedback = [1, 1, 0, 0, 0]  # C and R are in word but wrong positions
        result = trim_list("CRANE", feedback, candidates)
        # All results should have C and R, but not in positions 0 and 1
        for word in result:
            assert "C" in word
            assert "R" in word
            assert word[0] != "C"
            assert word[1] != "R"

    def test_trim_with_mixed_feedback(self):
        """Test trimming with mixed feedback."""
        candidates = ["CRANE", "PLANE", "CRATE", "SLATE", "REACT"]
        feedback = [1, 1, 2, 0, 1]  # C, R, E are cows, A is bull, N is absent
        result = trim_list("CRANE", feedback, candidates)
        # Results should:
        # - Have A in position 2 (bull)
        # - Have C, R, E but not in positions 0, 1, 4 (cows)
        # - Not have N (absent)
        for word in result:
            assert word[2] == "A"
            assert "C" in word and word[0] != "C"
            assert "R" in word and word[1] != "R"
            assert "E" in word and word[4] != "E"
            assert "N" not in word

    def test_trim_empty_candidates(self):
        """Test trimming with empty candidate list."""
        candidates = []
        feedback = [2, 2, 2, 2, 2]
        result = trim_list("CRANE", feedback, candidates)
        assert result == []

    def test_trim_no_matches(self):
        """Test trimming when no candidates match."""
        candidates = ["ABCDE", "FGHIJ"]
        feedback = [2, 2, 2, 2, 2]  # Perfect match for "CRANE"
        result = trim_list("CRANE", feedback, candidates)
        assert result == []

    def test_trim_duplicate_letter_excluded_position(self):
        """Test banns vs pawns: n at pos 2 got 0, must exclude words with n at 2."""
        candidates = ["pawns", "fawns", "banns", "yawns", "panns"]
        feedback = [0, 2, 0, 2, 2]  # banns vs pawns
        result = trim_list("banns", feedback, candidates)
        assert "pawns" in result
        assert "fawns" in result
        assert "yawns" in result
        assert "banns" not in result  # has b (absent)
        assert "panns" not in result  # has n at pos 2 (excluded_position)


class TestRandomWordSelect:
    """Tests for random_word_select function."""

    def test_select_default_number(self):
        """Test selecting default number of words."""
        candidates = ["CRANE", "PLANE", "CRATE", "SLATE"]
        result = random_word_select(candidates)
        assert len(result) == 20
        assert all(word in candidates for word in result)

    def test_select_specified_number(self):
        """Test selecting specified number of words."""
        candidates = ["CRANE", "PLANE", "CRATE", "SLATE"]
        result = random_word_select(candidates, num_words=5)
        assert len(result) == 5
        assert all(word in candidates for word in result)

    def test_select_zero_words(self):
        """Test selecting zero words."""
        candidates = ["CRANE", "PLANE", "CRATE", "SLATE"]
        result = random_word_select(candidates, num_words=0)
        assert result == []

    def test_select_allows_duplicates(self):
        """Test that selection allows duplicates."""
        candidates = ["CRANE", "PLANE"]
        result = random_word_select(candidates, num_words=10)
        assert len(result) == 10
        # With only 2 candidates and 10 selections, duplicates are guaranteed
        assert len(set(result)) <= 2

    def test_select_single_candidate(self):
        """Test selecting from single candidate."""
        candidates = ["CRANE"]
        result = random_word_select(candidates, num_words=5)
        assert result == ["CRANE", "CRANE", "CRANE", "CRANE", "CRANE"]

    def test_select_empty_candidates(self):
        """Test selecting from empty candidate list returns empty list."""
        candidates = []
        result = random_word_select(candidates, num_words=1)
        assert result == []
