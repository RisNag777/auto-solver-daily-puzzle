# Auto Solver for Daily Puzzle Games

An AI-powered agent that automatically solves Wordle and similar daily puzzle games using OpenAI's GPT-4o-mini. The agent intelligently filters candidate words based on game feedback and uses AI to suggest optimal guesses.

## 🎯 Features

- **AI-Powered Guessing**: Uses OpenAI's GPT-4o-mini to generate intelligent word guesses
- **Smart Filtering**: Automatically filters candidate words based on feedback (bulls, cows, and absent letters)
- **Feedback Analysis**: Categorizes letters into correct positions (bulls), wrong positions (cows), and absent letters
- **Constraint Satisfaction**: Ensures all guesses satisfy historical feedback constraints
- **Comprehensive Testing**: Full test suite for game logic functions
- **Duplicate Letter Handling**: Properly handles edge cases with duplicate letters in guesses and solutions

## 📋 Prerequisites

- Python 3.7 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- A word list file (`data/words.txt`) containing valid 5-letter words (one per line)

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd auto-solver-daily-puzzle-1
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   DATA_FOLDER=data  # Optional, defaults to "data"
   ```

4. **Verify word list**:
   Ensure `data/words.txt` exists and contains valid 5-letter words (one per line).

## 💻 Usage

### Running the Wordle Agent

To run the agent, you need to call the `wordle_agent()` function. You can do this in several ways:

**Option 1: Python interactive session**
```python
from src.wordle_agent import wordle_agent
wordle_agent()
```

**Option 2: Create a main script**
Create a file `main.py` in the project root:
```python
from src.wordle_agent import wordle_agent

if __name__ == "__main__":
    wordle_agent()
```

Then run:
```bash
python main.py
```

### How It Works

1. **Game Initialization**: The agent randomly selects a solution word from the word list and starts with a random initial guess.

2. **Feedback Generation**: For each guess, the agent receives feedback:
   - `2` (Bull): Letter is in the correct position
   - `1` (Cow): Letter is in the word but wrong position
   - `0` (Absent): Letter is not in the word

3. **Candidate Filtering**: The agent filters the word list based on feedback:
   - Removes words containing absent letters
   - Keeps only words with letters in correct positions (bulls)
   - Ensures letters marked as cows appear in different positions
   - Handles duplicate letters correctly

4. **AI-Guided Guessing**: The agent uses GPT-4o-mini to suggest the next guess based on:
   - Filtered candidate words
   - Historical feedback constraints
   - Common letter patterns and vowel usage
   - Wordle game rules

5. **Validation**: The agent validates AI suggestions against the filtered candidate list and retries if invalid.

6. **Victory**: The game ends when the solution is found or after 6 turns.

### Example Output

```
SOLUTION:  crane
GUESS:  stare
FEEDBACK:  [0, 1, 2, 1, 2]
REMAINING CANDIDATES:  42
[AI suggests next guess]
...
You've done it!
Your guess crane was the solution after all!
You finished in 4 turns!
```

## 📁 Project Structure

```
auto-solver-daily-puzzle-1/
├── data/
│   └── words.txt          # Word list (one 5-letter word per line)
├── src/
│   ├── __init__.py
│   ├── game_logic.py      # Core game logic (feedback, filtering)
│   └── wordle_agent.py    # AI agent implementation
├── tests/
│   ├── __init__.py
│   └── test_game_logic.py # Unit tests for game logic
├── .env                   # Environment variables (create this)
├── LICENSE                # Apache License 2.0
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🧪 Testing

Run the test suite using pytest:

```bash
pytest tests/
```

Or run with verbose output:

```bash
pytest tests/ -v
```

The test suite covers:
- Word list retrieval
- Feedback generation (including edge cases with duplicates)
- Candidate filtering
- Letter categorization (bulls, cows, absent)
- Random word selection

## 🔧 Core Functions

### `game_logic.py`

- **`retrieve_word_list()`**: Loads words from `data/words.txt`
- **`get_feedback(guess_list, solution_list)`**: Generates feedback array (0, 1, or 2 for each position)
- **`cow_bull_absent(guess, feedback)`**: Categorizes letters into bulls, cows, and absent
- **`trim_list(guess, feedback, candidates)`**: Filters candidates based on feedback
- **`random_word_select(candidates, num_words=20)`**: Selects random words for AI context

### `wordle_agent.py`

- **`wordle_agent()`**: Main game loop that manages the Wordle session
- **`feedback_explanation(turn, guess_list, feedback)`**: Generates human-readable feedback explanation
- **`extract_guess(ai_response_content)`**: Extracts guess from AI response using regex patterns

## 📦 Dependencies

- **openai**: OpenAI API client for GPT-4o-mini
- **python-dotenv**: Environment variable management
- **pytest**: Testing framework
- **black**: Code formatter (development)
- **flake8**: Linter (development)

See `requirements.txt` for specific versions.

## 🎮 Game Rules

The agent follows standard Wordle rules:

1. **Bulls (2)**: Letters in the correct position must remain in that position for all future guesses
2. **Cows (1)**: Letters in the word but wrong position must appear in a different position until they become bulls
3. **Absent (0)**: Letters not in the word must not appear in any future guesses
4. **Duplicate Letters**: Handles cases where a letter appears multiple times in guess or solution

## 🔍 How Feedback Works

Example: Guess = "CRANE", Solution = "PLANE"

- C (position 0): `0` - Not in solution
- R (position 1): `0` - Not in solution
- A (position 2): `2` - Correct position
- N (position 3): `2` - Correct position
- E (position 4): `2` - Correct position

Feedback: `[0, 0, 2, 2, 2]`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🐛 Troubleshooting

### Common Issues

1. **`FileNotFoundError` for `words.txt`**:
   - Ensure `data/words.txt` exists
   - Check that `DATA_FOLDER` environment variable is set correctly

2. **`OPENAI_API_KEY` not found**:
   - Create a `.env` file in the project root
   - Add `OPENAI_API_KEY=your_key_here`

3. **Invalid guess from AI**:
   - The agent will retry up to 5 times
   - If all attempts fail, it falls back to a random valid guess

4. **Import errors**:
   - Ensure you're running from the project root directory
   - Verify all dependencies are installed: `pip install -r requirements.txt`

## 🔮 Future Enhancements

Potential improvements:
- Support for other daily puzzle games (Quordle, Octordle, etc.)
- Performance statistics and analytics
- Different AI models or strategies
- Web interface
- Custom word list support
- Difficulty levels

## 📝 Notes

- The agent uses GPT-4o-mini with temperature=0 for deterministic results
- The word list should contain only valid 5-letter English words
- The agent automatically handles edge cases like duplicate letters
- All guesses are validated against the filtered candidate list

---

**Happy Wordling! 🎉**
