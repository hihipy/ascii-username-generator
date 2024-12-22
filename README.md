# ascii-username-generator

A Python-based graphical application that generates unique, ASCII-compliant usernames across multiple languages using WordNet. The application features a modern GUI interface with real-time logging, customizable formatting options, and clipboard integration.

## Features

- **Multi-Language Support**: Generates usernames from 19 different languages including English, Spanish, French, Italian, and more
- **Customizable Formatting**:
  - Case options: lowercase, UPPERCASE, or Capitalized
  - Optional numeric suffixes: single digit (0-9), double digit (00-99), or triple digit (000-999)
- **Real-Time Progress Display**: Visual feedback during username generation process
- **Clipboard Integration**: Click-to-copy functionality for easy username selection
- **ASCII Compliance**: Ensures generated usernames are compatible with most systems
- **Profanity Filtering**: Built-in protection against inappropriate content
- **Comprehensive Logging**: Both file-based and GUI-based logging for troubleshooting
- **Thread-Safe Operation**: Background processing prevents GUI freezing during generation

## Requirements

To run this application, you'll need Python 3.6+ and the following libraries:

```bash
pip install nltk
pip install better-profanity
pip install pyperclip
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/username-generator.git
cd username-generator
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python username_generator.py
```

## Usage

1. **Launch the Application**: Run the script to open the GUI interface
2. **Configure Settings**:
   - Select case style (lowercase, UPPERCASE, or Capitalized)
   - Choose numeric suffix option (none, single digit, double digit, or triple digit)
3. **Generate Usernames**: Click the "Generate Usernames" button
4. **View Results**: 
   - Generated usernames appear in the table with their source language
   - Click any username to copy it to clipboard
   - View generation progress in the log window

## Supported Languages

The generator supports username creation in the following languages:
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

### Architecture
- Built using Python's Tkinter for GUI
- Implements multi-threading for responsive user interface
- Uses NLTK's WordNet for word sourcing
- Includes comprehensive logging system with both file and GUI output

### Logging
- File logs stored in `username_generator.log`
- Real-time log display in GUI
- Different logging levels for debugging and general use

### Error Handling
- Graceful handling of resource loading failures
- User-friendly error messages
- Automatic NLTK resource downloading

## Acknowledgments

- [NLTK team](https://www.nltk.org/) for providing the WordNet database
- [Better-profanity](https://pypi.org/project/better-profanity/) library for content filtering 
- [Python Tkinter](https://docs.python.org/3/library/tkinter.html) documentation for GUI development guidance
- [Jimpix Username Generator](https://jimpix.co.uk/words/username-generator.php) for inspiration

---
[username-generator](https://github.com/yourusername/username-generator) © 2024 by Philip Bachas-Daunert is licensed under [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International](https://creativecommons.org/licenses/by-nc-nd/4.0/)
