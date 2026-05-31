# ascii-username-generator

[![Link Check](https://github.com/hihipy/ascii-username-generator/actions/workflows/links.yml/badge.svg)](https://github.com/hihipy/ascii-username-generator/actions/workflows/links.yml)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

**Built with**

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![NLTK](https://img.shields.io/badge/NLTK-154F5B?style=flat&logoColor=white)](https://www.nltk.org)
[![better-profanity](https://img.shields.io/badge/better--profanity-C0392B?style=flat&logoColor=white)](https://pypi.org/project/better-profanity/)
[![pyperclip](https://img.shields.io/badge/pyperclip-607D8B?style=flat&logoColor=white)](https://pypi.org/project/pyperclip/)
[![Tkinter](https://img.shields.io/badge/Tkinter-FFD43B?style=flat&logo=python&logoColor=black)](https://docs.python.org/3/library/tkinter.html)

A Python app with a GUI for generating unique, ASCII-compliant usernames in multiple languages using WordNet. Features real-time logging, customizable formatting, and clipboard integration.

## Features
- **Multi-Language Support:** Generates usernames in 19 languages, including English, Spanish, French, Italian, and more.
- **Customizable Formatting:**
  - Case options: lowercase, UPPERCASE, or Capitalized.
  - Numeric suffixes: none, single digit (0-9), double digit (00-99), or triple digit (000-999).
  - Generation size: Quick (10), Light (25), Standard (40), Large (75), or Heavy (150).
- **No Defaults:** All formatting options must be explicitly selected before generation runs.
- **Real-Time Progress Display:** Updates on the username generation process in a persistent console log.
- **Opt-In File Logging:** Log output is console-only by default. Check "Save log to file" to write logs to `ascii_username_generator.log`.
- **Clipboard Integration:** Click-to-copy usernames.
- **ASCII Compliance:** Ensures compatibility with most systems.
- **Profanity Filtering:** Built-in protection against inappropriate content.
- **Thread-Safe Operation:** Prevents freezing during generation.

## Requirements
Python 3.6+ and the following libraries:
```bash
pip install nltk better-profanity pyperclip
```

## Installation
1. Clone the repository:
```bash
git clone https://github.com/hihipy/ascii-username-generator.git
cd ascii-username-generator
```
2. Run the script:
```bash
python ascii_username_generator.py
```

## Usage
1. **Start the App:** Open the GUI by running the script.
2. **Choose Settings:**
   - Select a case style: lowercase, UPPERCASE, or Capitalized.
   - Pick a numeric suffix: none, single digit, double digit, or triple digit.
   - Pick a generation size: Quick, Light, Standard, Large, or Heavy.
3. **Generate Usernames:** Click "Generate Usernames." All three option groups must be selected or a warning will prompt you to complete them.
4. **View Results:**
   - Usernames appear in a table alongside their source language.
   - Click a username to copy it to the clipboard.
   - Progress is shown in the console log window.
5. **File Logging (optional):** Check "Save log to file" to write a detailed log to disk. Uncheck to stop. No file is created unless this is enabled.

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
- **GUI:** Built using Python's Tkinter.
- **Word Source:** Uses NLTK's WordNet database for word generation.
- **Real-Time Logs:** Displays generation progress in a persistent terminal-like console window.
- **File Logging:** Deferred — the `FileHandler` is only instantiated when the user enables it, so no log file is created on startup.
- **Multi-Threading:** Ensures the GUI remains responsive during generation.
- **Error Handling:** Automatic downloading of missing NLTK resources and user-friendly messages.

## Acknowledgments
- [NLTK](https://www.nltk.org/) - WordNet integration
- [Better-Profanity](https://pypi.org/project/better-profanity/) - Profanity filtering
- [Python's Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI framework
- [Jimpix Username Generator](https://jimpix.co.uk/words/username-generator.php) - Tool inspiration

## License
This project is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

You are free to:
- Use, share, and adapt this work
- Use it at your job

Under these terms:
- **Attribution** — Credit the original author
- **NonCommercial** — No selling or commercial products
- **ShareAlike** — Derivatives must use the same license