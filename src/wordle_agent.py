from collections import defaultdict
from dotenv import load_dotenv
from openai import OpenAI
import os
import random
import re

from src.game_logic import (
    get_feedback,
    retrieve_word_list,
    trim_list,
    random_word_select,
)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def feedback_explanation(turn, guess_list, feedback):
    """
    Generate a human-readable explanation of feedback from a Wordle guess.

    Creates a formatted string that explains the current game state and
    categorizes each letter in the guess based on the feedback:
    - Absent (0): Letters not in the solution
    - Cows (1): Letters in the solution but wrong position
    - Bulls (2): Letters in the correct position

    Args:
        turn (int): The current turn number (out of 6).
        guess (str): The 5-letter word that was guessed.
        feedback (list[int]): List of feedback values (0, 1, or 2) for each
                              position, typically from get_feedback().

    Returns:
        str: A formatted string explaining the turn, guess, feedback, and
             categorization of each letter with its position information.

    Example:
        >>> feedback_explanation(1, "CRANE", [0, 0, 2, 2, 2])
        "It is currently turn 1 out of 6.\\nThe guessed word is CRANE.\\n..."
    """
    fb_exp = f"""It is currently turn {turn} out of 6.\nThe guessed word is
    {guess_list}.\nThe feedback is {feedback}\n\n"""
    absent, bulls, cows = [], defaultdict(list), defaultdict(list)
    for i in range(5):
        if feedback[i] == 0:
            absent.append(guess_list[i])
        if feedback[i] == 1:
            cows[guess_list[i]].append(i)
        if feedback[i] == 2:
            bulls[guess_list[i]].append(i)

    fb_exp += f"""- The letters {', '.join(absent)} are not in the
    solution (0).\n"""
    for char, pos in bulls.items():
        fb_exp += f"""- The letter {char} is in the correct position (2) at
        index {pos}.\n"""
    for char, pos in cows.items():
        fb_exp += f"""- The letter {char} is in the solution but not in the
        correct position (1). Anywhere other than index {pos}.\n"""
    return fb_exp


def extract_guess(ai_response_content):
    patterns = [
        r"guess\s*:\s*['\"]?([a-zA-Z]{5})['\"]?",  # "guess: baker"
        r"guess['\"]?\s*:\s*['\"]([a-zA-Z]{5})['\"]",  # 'guess': 'baker'
        r"['\"]guess['\"]\s*:\s*['\"]([a-zA-Z]{5})['\"]",  # "guess": "baker"
    ]

    guess_object = None
    content_to_search = ai_response_content
    code_block_match = re.search(
        r"```(?:json|python)?\s*(.*?)```",
        content_to_search,  # fmt: off
        re.DOTALL | re.IGNORECASE,
    )
    if code_block_match:
        content_to_search = code_block_match.group(1)

    for pattern in patterns:
        guess_match = re.search(
            pattern, content_to_search, re.IGNORECASE | re.MULTILINE
        )
        if guess_match:
            guess_object = guess_match.group(1).lower()
            break
    return guess_object


def wordle_agent():
    """
    Run an interactive Wordle game session with AI-powered guess suggestions.

    Manages a complete Wordle game session where the user provides guesses
    and receives AI-generated suggestions for the next guess. The function:
    - Prompts the user for guesses each turn
    - Generates feedback for each guess
    - Filters candidate words based on feedback
    - Uses OpenAI's GPT-4o-mini to suggest next guesses
    - Tracks game history and provides victory message when solved

    The AI suggestions are based on:
    - Filtered candidate words that match all feedback constraints
    - Wordle game rules (bulls must stay in position, cows must move, etc.)
    - Common letter patterns and vowel usage
    - Valid English words only

    Args:
        solution (str): The 5-letter solution word that the user is trying
                        to guess.

    Returns:
        None: The function prints output and manages game state interactively.

    Note:
        - Requires OPENAI_API_KEY environment variable to be set
        - Game runs for up to 6 turns
        - Requires user input via stdin for each guess
        - Uses retrieve_word_list() to get initial candidate pool (must be
          called before first trim_list call)

    Example:
        >>> wordle_agent("CRANE")
        Enter your guess - STARE
        [AI suggests next guess based on feedback]
        ...
    """
    history = {}
    candidates = retrieve_word_list()
    solution = random.choice(candidates)
    print("SOLUTION: ", solution)
    guess = random.choice([w for w in candidates if w != solution])
    for turn in range(6):
        guess_list = list(guess)
        print("GUESS: ", guess)
        solution_list = list(solution)
        feedback = get_feedback(guess_list, solution_list)
        print("FEEDBACK: ", feedback)
        fb_exp = feedback_explanation(turn, guess_list, feedback)
        history[guess] = feedback
        if guess == solution:
            Response = f"""
            You've done it!
            Your guess {guess} was the solution after all!
            You finished in {turn + 1} turns!
            Your game played out as follows -
            {history}
            """
            print(Response)
            break
        candidates = trim_list(guess, feedback, candidates)
        print("REMAINING CANDIDATES: ", len(candidates))
        random_candidates = random_word_select(candidates)
        wordle_words = ", ".join(random_candidates)
        Prompt = f"""You are acting as WordleBot.
        Wordle is a game that has a predetermined 5 letter word as the
        solution.
        The user needs to guess what the solution is and they have 6 guesses
        to do so.
        You will receive a 5 letter word as the previous guess but in the
        format of a list with 5 characters in it
        Your aim is to help the user get to the solution quickly by giving
        the next guess that the user should try.
        The best case scenario is if your guess exactly matches the solution.

        <data_definition>
        For a given guess, you will be provided with the feedback.
        Feedback is a list containing 5 items that are 0, 1 or 2.
        0 implies that the corresponding letter is not present in the
        solution.
        1 implies that the corresponding letter is present at a different
        position in the solution.
        2 implies that the corresponding letter is present in the solution
        and is in the correct position.

        Example
        Guess = 'adieu', Solution = 'bidet'
        Feedback = [0, 1, 1, 2, 0]
        This means that 'a' and 'u' are not in the solution
        'd' and 'i' are in the solution but are not at positions 2 and 3
        respectively
        'e' is in the solution and is in the right position.
        A good next guess would be a word like 'dices' since it satisfies all
        the above criteria ie, 'a' and 'u' are not in the solution,
        'd' and 'i' are not present in the same positions as in 'adieu' and
        'e' is in the correct position.
        </data_definition>

        The current user guess is {guess_list} and feedback is {feedback},
        which means {fb_exp}.
        Given that there could be infinite guesses, there is a corpus
        containing words used in wordle.
        There is a tool to eliminate all words that do not meet the feedback
        criteria from this corpus.

        Example
        Words like 'arrow' and 'weary' are removed from the corpus because
        'a' should not be present, 'e' should be in the 4th position, 'd' and
        'i' should be present

        <choosing_a_good_guess>
        1. These 20 words {wordle_words} are randomly chosen from the
        remaining corpus of valid words. Words like these are good guesses
        2. Try to pick words with common letters like s,t,h,r,y
        3. Most words have atleast one vowel - a,e,i,o,u. So try to provide
        guesses with vowels to maximize match criteria.
        4. Every guess needs to be a real English word
        5. Proper nouns are invalid guesses
        </choosing_a_good_guess>

        <guess_rules>
        1. When feedback for a character is 2, then that character MUST be
        present in THE SAME POSITION for all future guesses.
        2. When feedback for a character is 1, then that character MUST be
        present in a different position to gain new information
        UNTIL feedback changes to 2 after which, it MUST be present in THE
        SAME POSITION for all future guesses.
        3. When feedback for a character is 0, it MUST NOT BE in ANY future
        guesses.
        </guess_rules>

        <response_format>
        guess: your chosen guess should be a 5 letter word that matches all
        the above constraints.
        <response_format>

        Strict absolute constraints you cannot miss
        1. Your guess should STRICTLY SATISFY the rules above.
        2. Your guess needs to be a real English word
        3. Your guess HAS to be a 5 letter word
        """
        valid_guess = True
        messages = [{"role": "user", "content": guess}]
        messages.append({"role": "system", "content": Prompt})
        valid_check = 0
        while valid_guess:
            valid_check += 1
            completion = client.chat.completions.create(
                model="gpt-4o-mini", messages=messages, temperature=0
            )
            ai_response_content = completion.choices[0].message.content
            messages.append(
                {
                    "role": "assistant",  # fmt: off
                    "content": ai_response_content,
                }  # fmt: off
            )
            print(ai_response_content)
            tmp_guess = extract_guess(ai_response_content)
            print("AGENT GUESS: ", tmp_guess)
            if tmp_guess in candidates:
                guess = tmp_guess
                break
            else:
                if valid_check == 5:
                    guess = random.choice(
                        [w for w in candidates if w != solution]  # fmt: off
                    )
                    print("Agent unable to pick valid guess.")
                    print(f"Random guess: {guess}")
                    break
                else:
                    invalid_guess_prompt = f"""Your guess {tmp_guess} is not
                    valid as it does not satisfy all the historical
                    constraints. For your reference, here are the historical
                    constraints - {history}.
                    Please make sure that the guess that you select satisfies
                    all the past constraints."""
                    messages.append(
                        {
                            "role": "system",  # fmt: off
                            "content": invalid_guess_prompt,
                        }  # fmt: off
                    )
