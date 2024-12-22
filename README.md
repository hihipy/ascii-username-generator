# [ascii-username-generator](https://github.com/hihipy/ascii-username-generator)

A Python app with a modern GUI for generating unique, ASCII-compliant usernames in multiple languages using WordNet. Features include real-time logging, customizable formatting, and clipboard integration.

## Features

- **Multi-Language Support**: Generates usernames in 19 languages, including English, Spanish, French, Italian, and more.
- **Customizable Formatting**: 
  - Case options: lowercase, UPPERCASE, or Capitalized.
  - Numeric suffixes: none, single digit (0-9), double digit (00-99), or triple digit (000-999).
- **Real-Time Progress Display**: Updates on the username generation process.
- **Clipboard Integration**: Click-to-copy usernames.
- **ASCII Compliance**: Ensures compatibility with most systems.
- **Profanity Filtering**: Built-in protection against inappropriate content.
- **Logging**: Real-time GUI logs and detailed file-based logs.
- **Thread-Safe Operation**: Prevents freezing during generation.

## Requirements

Ensure Python 3.6+ is installed, then run the following to install required libraries:

```bash
pip install nltk better-profanity pyperclip
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/hihipy/ascii-username-generator.git
cd username-generator
```

2. Run the script:
```bash
python username_generator.py
```

## Usage

1. Start the App: Open the GUI by running the script.
2. Choose Settings:
   - Select case style: lowercase, UPPERCASE, or Capitalized.
   - Pick numeric suffix options: none, single digit, double digit, or triple digit.
3. Generate Usernames: Click "Generate Usernames."
4. View Results:
   - Usernames appear in a table alongside their source language.
   - Click a username to copy it to the clipboard.
   - Progress is shown in the log window.

## Supported Languages

Generates usernames from the following languages:

- English
- Spanish
- French
- Italian
- Portuguese
- Dutch
- Polish
- Swedish
- Finnish
- Norwegian (Nynorsk)
- Norwegian (Bokmål)
- Romanian
- Slovak
- Slovenian
- Malay
- Basque
- Catalan
- Danish
- Lithuanian

## Technical Details

- GUI: Built using Python's Tkinter for an intuitive user interface.
- Word Source: Utilizes NLTK's WordNet database for word generation.
- Real-Time Logs: Displays generation progress in a terminal-like window.
- Multi-Threading: Ensures the GUI remains responsive during generation.
- Error Handling: Automatic downloading of missing NLTK resources and user-friendly messages.

## Acknowledgments

- [NLTK](https://www.nltk.org/) for WordNet integration
- [Better-Profanity](https://pypi.org/project/better-profanity/) for filtering
- [Python's Tkinter](https://docs.python.org/3/library/tkinter.html) documentation for GUI development guidance
- [Jimpix Username Generator](https://jimpix.co.uk/words/username-generator.php) for tool inspiration

---

ascii-username-generator © 2024 by Philip Bachas-Daunert is licensed under [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International](https://creativecommons.org/licenses/by-nc-nd/4.0/)
