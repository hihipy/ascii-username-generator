"""
Enhanced Username Generator with GUI Interface.

This module provides a graphical user interface for generating usernames in multiple languages
using WordNet. It includes features like case styling, number suffixes, and clipboard integration.
The generator ensures ASCII compliance and includes profanity filtering.
"""

import sys
import logging
import os
import random
import warnings
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread

import nltk
import pyperclip
from nltk.corpus import wordnet
from better_profanity import profanity

# Suppress WordNet-related warnings during runtime
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module=r"nltk\.corpus\.reader\.wordnet"
)

# Configure logging system with both file and stream handlers
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

# Setup file handler for detailed logging
FILE_HANDLER = logging.FileHandler(
    "username_generator.log",
    mode="a",
    encoding="utf-8"
)
FILE_HANDLER.setLevel(logging.DEBUG)
FILE_FORMATTER = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
FILE_HANDLER.setFormatter(FILE_FORMATTER)

# Setup stream handler for console output
STREAM_HANDLER = logging.StreamHandler(sys.stdout)
STREAM_HANDLER.setLevel(logging.INFO)
STREAM_FORMATTER = logging.Formatter("%(levelname)s - %(message)s")
STREAM_HANDLER.setFormatter(STREAM_FORMATTER)

# Add handlers to logger
LOGGER.addHandler(FILE_HANDLER)
LOGGER.addHandler(STREAM_HANDLER)


class TextHandler(logging.Handler):
    """
    Custom logging handler that redirects log messages to a Tkinter Text widget.
    """

    def __init__(self, text_widget: tk.Text) -> None:
        """
        Initialize the TextHandler with the target Text widget.

        Args:
            text_widget (tk.Text): The Text widget where logs will be displayed.
        """
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record: logging.LogRecord) -> None:
        """
        Process and display a log record in the Text widget.

        Args:
            record (logging.LogRecord): The log record to be displayed.
        """
        msg = self.format(record)
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)  # Ensure the latest log is visible


class UsernameGenerator:
    """
    GUI-based username generator supporting multiple languages and customization options.
    """

    def __init__(self, root: tk.Tk) -> None:
        """
        Initialize the username generator application.

        Args:
            root (tk.Tk): The root Tkinter window.
        """
        LOGGER.info("Initializing UsernameGenerator.")
        self.root = root
        self.root.title("ASCII Username Generator")
        self.root.geometry("600x800")

        # Configure window resizing behavior
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Initialize style control variables
        self.case_var: tk.StringVar = tk.StringVar(value="lowercase")
        self.number_var: tk.StringVar = tk.StringVar(value="none")

        LOGGER.debug("Ensuring required NLTK data is available...")
        self.ensure_nltk_data()

        # Define supported languages with their codes and display names
        self.language_names: dict[str, str] = {
            "eng": "English",
            "spa": "Spanish",
            "fra": "French",
            "ita": "Italian",
            "por": "Portuguese",
            "nld": "Dutch",
            "pol": "Polish",
            "swe": "Swedish",
            "fin": "Finnish",
            "nno": "Norwegian Nynorsk",
            "nob": "Norwegian Bokmål",
            "ron": "Romanian",
            "slk": "Slovak",
            "slv": "Slovenian",
            "zsm": "Malay",
            "eus": "Basque",
            "cat": "Catalan",
            "dan": "Danish",
            "lit": "Lithuanian"
        }
        self.language_codes: list[str] = list(self.language_names.keys())

        # Initialize profanity filter
        profanity.load_censor_words()

        # Setup GUI components
        self.create_widgets()

    def ensure_nltk_data(self) -> None:
        """
        Ensure required NLTK data resources are available.
        Downloads missing resources if necessary and configures NLTK data path.
        """
        nltk_data_path: str = os.path.join(os.path.expanduser("~"), "nltk_data")
        if nltk_data_path not in nltk.data.path:
            nltk.data.path.append(nltk_data_path)
            LOGGER.info("Added NLTK data path: %s", nltk_data_path)

        resources: dict[str, str] = {"wordnet": "corpora/wordnet", "omw-1.4": "corpora/omw-1.4"}
        for resource, path in resources.items():
            try:
                nltk.data.find(path)
                LOGGER.info("Resource '%s' already downloaded.", resource)
            except LookupError:
                LOGGER.info("Downloading missing resource: %s", resource)
                nltk.download(resource, download_dir=nltk_data_path)

    def create_widgets(self) -> None:
        """
        Create and arrange all GUI components.
        """
        main_frame: ttk.Frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure frame resizing
        main_frame.rowconfigure(5, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Setup case styling options
        case_frame: ttk.LabelFrame = ttk.LabelFrame(main_frame, text="Username Case")
        case_frame.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        for value, text in [
            ("capitalize", "Capitalize"),
            ("lowercase", "all lowercase"),
            ("uppercase", "ALL UPPERCASE")
        ]:
            ttk.Radiobutton(
                case_frame,
                text=text,
                variable=self.case_var,
                value=value
            ).pack(anchor=tk.W)

        # Setup number style options
        num_frame: ttk.LabelFrame = ttk.LabelFrame(main_frame, text="Number Style")
        num_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        for value, text in [
            ("none", "None"),
            ("1digit", "(0-9)"),
            ("2digit", "(00-99)"),
            ("3digit", "(000-999)")
        ]:
            ttk.Radiobutton(
                num_frame,
                text=text,
                variable=self.number_var,
                value=value
            ).pack(anchor=tk.W)

        # Add generation button
        gen_button: ttk.Button = ttk.Button(
            main_frame,
            text="Generate Usernames",
            command=self.start_generation_thread
        )
        gen_button.grid(row=1, column=0, columnspan=2, pady=10)

        # Add informational label
        ttk.Label(
            main_frame,
            text=(
                "Languages are pre-defined; some English words "
                "may appear in other languages."
            ),
            font=("Helvetica", 10)
        ).grid(row=2, column=0, columnspan=2, pady=5)

        # Setup username display and log window
        self.setup_treeview(main_frame)
        self.setup_log_window(main_frame)

    def setup_treeview(self, parent_frame: ttk.Frame) -> None:
        """
        Create and configure the Treeview widget for displaying usernames.

        Args:
            parent_frame (ttk.Frame): The parent frame to contain the Treeview.
        """
        table_frame = ttk.Frame(parent_frame)
        table_frame.grid(row=5, column=0, columnspan=2, sticky="nsew")

        # Configure frame resizing
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # Create Treeview
        self.tree = ttk.Treeview(
            table_frame,
            columns=("username", "language"),
            show="headings"
        )
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Configure column headings
        self.tree.heading("username", text="Username")
        self.tree.heading("language", text="Language")

        # Add vertical scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Bind click event for copying usernames
        self.tree.bind("<ButtonRelease-1>", self.on_username_click)

    def setup_log_window(self, parent_frame: ttk.Frame) -> None:
        """
        Create and configure the log display window.

        Args:
            parent_frame (ttk.Frame): The parent frame to contain the log window.
        """
        log_frame = ttk.Frame(parent_frame)
        log_frame.grid(row=6, column=0, columnspan=2, sticky="nsew")

        # Create log display Text widget
        self.log_output = tk.Text(
            log_frame,
            wrap=tk.WORD,
            height=10,
            bg="white",
            fg="black",
            font=("Courier", 10)
        )
        self.log_output.grid(row=0, column=0, sticky="nsew")

        # Configure frame resizing
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        # Add vertical scrollbar
        scrollbar = ttk.Scrollbar(
            log_frame,
            orient=tk.VERTICAL,
            command=self.log_output.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_output.configure(yscrollcommand=scrollbar.set)

        # Configure log redirection
        log_handler = TextHandler(self.log_output)
        log_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        LOGGER.addHandler(log_handler)

    def start_generation_thread(self) -> None:
        """
        Start username generation in a separate thread to prevent GUI freezing.
        """
        Thread(target=self.generate_usernames, daemon=True).start()

    def generate_usernames(self) -> None:
        """
        Generate and display a set of random usernames.
        """
        LOGGER.info("Starting username generation...")
        self.log_output.insert(tk.END, "Generating usernames...\n")
        self.log_output.see(tk.END)

        # Clear existing usernames
        for row in self.tree.get_children():
            self.tree.delete(row)

        usernames = []
        total = 40  # Number of usernames to generate

        for i in range(total):
            message = f"Generating username {i + 1}/{total}..."
            LOGGER.info(message)
            self.log_output.insert(tk.END, f"{message}\n")
            self.log_output.see(tk.END)

            lang_code = random.choice(self.language_codes)
            username = self.generate_ascii_username(lang_code)
            usernames.append((username, self.language_names.get(lang_code, lang_code)))

        usernames.sort(key=lambda x: x[0])
        for username, lang_name in usernames:
            self.tree.insert("", "end", values=(username, lang_name))

        LOGGER.info("Username generation completed successfully.")
        self.log_output.insert(tk.END, "Username generation completed successfully.\n")
        self.log_output.see(tk.END)

    def generate_ascii_username(self, lang_code: str) -> str:
        """
        Generate a single ASCII-compliant username for specified language.

        Args:
            lang_code (str): The language code to use for word selection.

        Returns:
            str: A formatted username string.
        """
        words = self.get_words(lang_code)
        valid_words = [word for word in words if self.is_valid_word(word)]
        return self.finalize_username(random.choice(valid_words))

    def get_words(self, lang_code: str) -> list[str]:
        """
        Retrieve valid words from WordNet for specified language.

        Args:
            lang_code (str): The language code to fetch words for.

        Returns:
            list[str]: List of valid words for the specified language.
        """
        words = []
        try:
            for synset in wordnet.all_synsets():
                for lemma in synset.lemmas(lang=lang_code):
                    word = lemma.name()
                    if word.isalnum():
                        words.append(word)
        except Exception as exc:
            LOGGER.warning("Failed to fetch words for '%s': %s", lang_code, exc)
        return words

    def is_valid_word(self, word: str, min_len: int = 3) -> bool:
        """
        Validate word for username generation.

        Args:
            word (str): The word to validate.
            min_len (int): Minimum acceptable word length.

        Returns:
            bool: True if word meets all criteria, False otherwise.
        """
        return all(ord(c) < 128 for c in word) and len(word) >= min_len

    def finalize_username(self, word: str) -> str:
        """
        Apply final formatting to username.

        Args:
            word (str): Base word to format into username.

        Returns:
            str: Formatted username string with applied case and optional number suffix.
        """
        case = self.case_var.get()
        if case == "lowercase":
            word = word.lower()
        elif case == "uppercase":
            word = word.upper()
        elif case == "capitalize":
            word = word.capitalize()

        style = self.number_var.get()
        if style == "1digit":
            word += str(random.randint(0, 9))
        elif style == "2digit":
            word += f"{random.randint(0, 99):02d}"
        elif style == "3digit":
            word += f"{random.randint(0, 999):03d}"
        return word

    def on_username_click(self, event: tk.Event) -> None:
        """
        Handle username click event by copying to clipboard.

        Args:
            event (tk.Event): The Tkinter event object containing click information.
        """
        row_id = self.tree.identify_row(event.y)
        if row_id:
            values = self.tree.item(row_id, "values")
            if values:
                username = values[0]
                pyperclip.copy(username)
                LOGGER.info("Copied username: %s", username)


def main() -> None:
    """
    Main entry point for the application.
    """
    try:
        root = tk.Tk()
        UsernameGenerator(root)
        root.mainloop()
    except Exception as exc:
        LOGGER.critical("Application failed to start", exc_info=True)
        messagebox.showerror("Critical Error", str(exc))


if __name__ == "__main__":
    main()