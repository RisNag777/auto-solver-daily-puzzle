from collections import defaultdict
from dotenv import load_dotenv
from openai import OpenAI
import os

from src.game_logic import (
    get_feedback,
    retrieve_word_list,
    trim_list,
    random_word_select,
)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def feedback_explanation(turn, guess, feedback):
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
    {guess}.\nThe feedback is {feedback}\n\n"""
    absent, bulls, cows = [], defaultdict(list), defaultdict(list)
    for i in range(5):
        if feedback[i] == 0:
            absent.append(guess[i])
        if feedback[i] == 1:
            cows[guess[i]].append(i)
        if feedback[i] == 2:
            bulls[guess[i]].append(i)

    fb_exp += f"""- The letters {', '.join(absent)} are not in the
    solution (0).\n"""
    for char, pos in bulls.items():
        fb_exp += f"""- The letter {char} is in the correct position (2) at
        index {pos}.\n"""
    for char, pos in cows.items():
        fb_exp += f"""- The letter {char} is in the solution but not in the
        correct position (1). Anywhere other than index {pos}.\n"""
    return fb_exp


def wordle_agent(solution):
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
    solution = input("Enter the solution word - ")
    history = {}
    for turn in range(6):
        guess = input("Enter your guess - ")
        feedback = get_feedback(guess, solution)
        fb_exp = feedback_explanation(turn, guess, feedback)
        history[guess] = feedback
        if guess == solution:
            Response = f"""You've done it!
            Your guess {guess} was the solution after all!
            You finished in {turn + 1} turns!
            Your game played out as follows -
            {history}"""
            print(Response)
            break
        candidates = retrieve_word_list()
        candidates = trim_list(guess, feedback, candidates)
        random_candidates = random_word_select(candidates)
        wordle_words = ", ".join(random_candidates)
        Prompt = f"""You are acting as WordleBot.
        Wordle is a game that has a predetermined 5 letter word as the
        solution.
        The user needs to guess what the solution is and they have 6 guesses
        to do so.
        Your aim is to help the user get to the solution quickly by giving
        the next guess that the user should try.
        The best case scenario is if your guess exactly matches the solution.

        <data_definition>
        For a given guess, you will be provided with the feedback.
        Feedback is a list containing 5 items that are 0, 1 or 2.
        0 implies that the corresponding letter not present in the solution.
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

        The current user guess is {guess} and feedback is {feedback}, which
        means {fb_exp}.
        Given that there could be infinite guesses, there is a corpus
        containing words used in wordle.
        There is a tool to eliminate all words that do not meet the feedback
        criteria from this corpus.

        Example
        Words like 'arrow' is removed from the corpus because 'a' should not
        be present, 'e' should be in the 4th position, 'd' and 'i' should be
        present

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

        <reason>
        1. Include feedback for your guess.
        2. Explain how your guess satisfies the guess rules.
        </reason>

        <response_format>
        guess: your chosen guess should be a 5 letter word that matches all
        the above constraints.
        reason: explain why you chose this guess

        Strict absolute constraints you cannot miss
        1. Your guess should STRICTLY SATISFY the rules above.
        2. Your guess needs to be a real English word
        3. Your guess HAS to be a 5 letter word
        """
        messages = [{"role": "user", "content": guess}]
        messages.append({"role": "system", "content": Prompt})
        completion = client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, temperature=0
        )
        ai_response_content = completion.choices[0].message.content
        messages.append({"role": "assistant", "content": ai_response_content})
        print(ai_response_content)
