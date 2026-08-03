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
import zipfile
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
from typing import cast

# nltk 3.10.1 ships an import finder (nltk/inisec.py) that blocks any module
# resolving to a path beneath the current working directory. It tests with
# Path.relative_to, so a venv nested under $HOME trips it whenever the process
# runs from $HOME, even when nothing is shadowing the module. PYTHONSAFEPATH
# does not help: the check reads the cwd directly rather than sys.path.
# This must run before nltk is first imported in the process.
# Revisit once nltk fixes the containment test.
os.environ["NLTK_DISABLE_IMPORT_SECURITY"] = "1"

# An earlier import in the same interpreter may have installed the finder
# already, since IPython and Jupyter reuse the process across runs. Strip any
# live instance so a rerun in an existing session is not still blocked.
_inisec = sys.modules.get("nltk.inisec")
if _inisec is not None:
	_finder_cls = getattr(_inisec, "NLTKSafeImportFinder", None)
	if _finder_cls is not None:
		sys.meta_path[:] = [
			finder for finder in sys.meta_path
			if not isinstance(finder, _finder_cls)
		]

import nltk  # noqa: E402
import pyperclip  # noqa: E402
from nltk.corpus import wordnet  # noqa: E402
from better_profanity import profanity  # noqa: E402

# Suppress WordNet-related warnings during runtime
warnings.filterwarnings(
	"ignore",
	category=UserWarning,
	module=r"nltk\.corpus\.reader\.wordnet"
)

# Configure logging system with stream handler only; file handler is created on demand
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Setup stream handler for console output
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_formatter = logging.Formatter("%(levelname)s - %(message)s")
stream_handler.setFormatter(stream_formatter)
logger.addHandler(stream_handler)


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
		logger.info("Initializing UsernameGenerator.")
		self.root = root
		self.root.title("ASCII Username Generator")
		self.root.geometry("900x800")

		# Configure window resizing behavior
		self.root.rowconfigure(0, weight=1)
		self.root.columnconfigure(0, weight=1)

		# Initialize style control variables — no defaults; user must select all three
		self.case_var: tk.StringVar = tk.StringVar(value="")
		self.number_var: tk.StringVar = tk.StringVar(value="")
		self.count_var: tk.StringVar = tk.StringVar(value="")
		self.log_var: tk.BooleanVar = tk.BooleanVar(value=False)  # File logging off by default

		# Widget references — cast(T, None) satisfies the type checker without | None cascades;
		# all three are fully assigned during create_widgets() before any other code runs.
		self.tree: ttk.Treeview = cast(ttk.Treeview, cast(object, None))
		self.log_output: tk.Text = cast(tk.Text, cast(object, None))
		self.log_frame: ttk.Frame = cast(ttk.Frame, cast(object, None))
		self._file_handler: logging.FileHandler | None = None

		# Per-language word lists, filled on first use. Walking all of WordNet is
		# expensive and the result does not change during a session.
		self._word_cache: dict[str, list[str]] = {}

		logger.debug("Ensuring required NLTK data is available...")
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

	@staticmethod
	def _resource_available(resource_path: str) -> bool:
		"""
		Report whether NLTK can resolve a corpus by its bare path.

		Args:
			resource_path (str): NLTK resource path, e.g. "corpora/wordnet".

		Returns:
			bool: True if nltk.data.find() resolves the path.
		"""
		try:
			nltk.data.find(resource_path)
			return True
		except LookupError:
			return False

	@staticmethod
	def _unpack_if_zipped(resource_path: str) -> bool:
		"""
		Extract <resource>.zip in place when the bare corpus name will not resolve.

		nltk 3.10.1 stopped resolving corpus names through their zip archives, so a
		corpus the downloader reports as up to date can sit on disk as a zip that
		nltk.data.find() calls missing. Extracting alongside the archive restores
		the bare-name lookup. The archives come from NLTK's own download servers.

		Args:
			resource_path (str): NLTK resource path, e.g. "corpora/wordnet".

		Returns:
			bool: True if an archive was found and extracted.
		"""
		try:
			zip_path = str(nltk.data.find(resource_path + ".zip"))
		except LookupError:
			return False

		target_dir = os.path.dirname(zip_path)
		logger.info("Unpacking %s into %s", os.path.basename(zip_path), target_dir)
		try:
			with zipfile.ZipFile(zip_path) as archive:
				archive.extractall(target_dir)
		except (OSError, zipfile.BadZipFile) as exc:
			logger.warning("Could not extract %s: %s", zip_path, exc)
			return False
		return True

	@staticmethod
	def ensure_nltk_data() -> None:
		"""
		Ensure required NLTK data resources are available.

		For each resource, tries in order: resolve it, unpack a zip already on
		disk, download it, unpack what was downloaded. Logs an error rather than
		raising if a resource is still unreachable, so the GUI still opens.
		"""
		nltk_data_path: str = os.path.join(os.path.expanduser("~"), "nltk_data")
		if nltk_data_path not in nltk.data.path:
			nltk.data.path.append(nltk_data_path)
			logger.info("Added NLTK data path: %s", nltk_data_path)

		# omw-2.0 is what synset.lemmas(lang=...) reads under nltk 3.10.1.
		# An older omw-1.4 on disk is harmless but is not a substitute.
		resources: dict[str, str] = {
			"wordnet": "corpora/wordnet",
			"omw-2.0": "corpora/omw-2.0",
		}

		for resource, path in resources.items():
			if UsernameGenerator._resource_available(path):
				logger.info("Resource '%s' already available.", resource)
				continue

			if UsernameGenerator._unpack_if_zipped(path):
				if UsernameGenerator._resource_available(path):
					logger.info("Resource '%s' restored from local archive.", resource)
					continue

			logger.info("Downloading missing resource: %s", resource)
			try:
				nltk.download(resource, download_dir=nltk_data_path)
			except Exception as exc:
				logger.error("Download of '%s' failed: %s", resource, exc)
				continue

			if UsernameGenerator._resource_available(path):
				continue
			if UsernameGenerator._unpack_if_zipped(path):
				if UsernameGenerator._resource_available(path):
					continue

			logger.error(
				"Resource '%s' is still unavailable after download and unpack. "
				"Languages relying on it will be skipped.", resource
			)

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
		case_frame.grid(row=0, column=0, sticky="w", padx=5, pady=5)
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
			).pack(anchor="w")

		# Setup number style options
		num_frame: ttk.LabelFrame = ttk.LabelFrame(main_frame, text="Number Style")
		num_frame.grid(row=0, column=1, sticky="w", padx=5, pady=5)
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
			).pack(anchor="w")

		# Setup generation size options
		size_frame: ttk.LabelFrame = ttk.LabelFrame(main_frame, text="Generation Size")
		size_frame.grid(row=0, column=2, sticky="w", padx=5, pady=5)
		for value, text in [
			("10", "Quick    (10)"),
			("25", "Light    (25)"),
			("40", "Standard (40)"),
			("75", "Large    (75)"),
			("150", "Heavy   (150)"),
		]:
			ttk.Radiobutton(
				size_frame,
				text=text,
				variable=self.count_var,
				value=value
			).pack(anchor="w")

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

		# Add file logging toggle checkbox (disabled by default)
		ttk.Checkbutton(
			main_frame,
			text="Save log to file",
			variable=self.log_var,
			command=self._toggle_file_logging
		).grid(row=3, column=0, columnspan=3, sticky="w", padx=5)

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
			orient="vertical",
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
		self.log_frame = log_frame  # Store reference for show/hide toggle

		# Create log display Text widget
		self.log_output = tk.Text(
			log_frame,
			wrap="word",
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
			orient="vertical",
			command=self.log_output.yview
		)
		scrollbar.grid(row=0, column=1, sticky="ns")
		self.log_output.configure(yscrollcommand=scrollbar.set)

		# Configure log redirection
		log_handler = TextHandler(self.log_output)
		log_handler.setFormatter(
			logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
		)
		logger.addHandler(log_handler)

	def _toggle_file_logging(self) -> None:
		"""Create and attach (or detach) the file handler based on the checkbox."""
		if self.log_var.get():
			file_handler = logging.FileHandler(
				"ascii_username_generator.log",
				mode="a",
				encoding="utf-8"
			)
			file_handler.setLevel(logging.DEBUG)
			file_handler.setFormatter(
				logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
			)
			self._file_handler = file_handler
			logger.addHandler(self._file_handler)
			logger.info("File logging enabled: ascii_username_generator.log")
		else:
			if self._file_handler is not None:
				handler = self._file_handler
				logger.removeHandler(handler)
				handler.close()
				self._file_handler = None

	def start_generation_thread(self) -> None:
		"""
		Start username generation in a separate thread to prevent GUI freezing.
		"""
		Thread(target=self.generate_usernames, daemon=True).start()

	def generate_usernames(self) -> None:
		"""
		Generate and display a set of random usernames.
		"""
		# Validate that all options have been selected before proceeding
		missing = []
		if not self.case_var.get():
			missing.append("Username Case")
		if not self.number_var.get():
			missing.append("Number Style")
		if not self.count_var.get():
			missing.append("Generation Size")
		if missing:
			messagebox.showwarning(
				"Missing Options",
				f"Please select an option for: {', '.join(missing)}"
			)
			return

		logger.info("Starting username generation...")
		self.log_output.insert(tk.END, "Generating usernames...\n")
		self.log_output.see(tk.END)

		# Clear existing usernames
		for row in self.tree.get_children():
			self.tree.delete(row)

		usernames = []
		total = int(self.count_var.get())

		# Languages that yield nothing usable are dropped for the rest of the run,
		# so one empty corpus cannot consume every attempt.
		available_codes = list(self.language_codes)

		for i in range(total):
			if not available_codes:
				logger.error("No language has usable words. Stopping generation.")
				break

			message = f"Generating username {i + 1}/{total}..."
			logger.info(message)
			self.log_output.insert(tk.END, f"{message}\n")
			self.log_output.see(tk.END)

			lang_code = random.choice(available_codes)
			username = self.generate_ascii_username(lang_code)
			if username is None:
				available_codes.remove(lang_code)
				continue
			usernames.append((username, self.language_names.get(lang_code, lang_code)))

		usernames.sort(key=lambda x: x[0])
		for username, lang_name in usernames:
			self.tree.insert("", "end", values=(username, lang_name))

		if len(usernames) < total:
			shortfall = (
				f"Generated {len(usernames)} of {total} requested; "
				"some languages had no usable words."
			)
			logger.warning(shortfall)
			self.log_output.insert(tk.END, f"{shortfall}\n")
		else:
			logger.info("Username generation completed successfully.")
			self.log_output.insert(tk.END, "Username generation completed successfully.\n")
		self.log_output.see(tk.END)

	def generate_ascii_username(self, lang_code: str) -> str | None:
		"""
		Generate a single ASCII-compliant username for specified language.

		Args:
			lang_code (str): The language code to use for word selection.

		Returns:
			str | None: A formatted username, or None if the language yields no
			usable words.
		"""
		valid_words = self._word_cache.get(lang_code)
		if valid_words is None:
			words = self.get_words(lang_code)
			valid_words = [word for word in words if self.is_valid_word(word)]
			self._word_cache[lang_code] = valid_words
			logger.debug(
				"Cached %d usable words for '%s' (from %d lemmas).",
				len(valid_words), lang_code, len(words)
			)

		if not valid_words:
			logger.warning("No usable words for '%s'; dropping it from this run.", lang_code)
			return None

		return self.finalize_username(random.choice(valid_words))

	@staticmethod
	def get_words(lang_code: str) -> list[str]:
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
			logger.warning("Failed to fetch words for '%s': %s", lang_code, exc)
		return words

	@staticmethod
	def is_valid_word(word: str, min_len: int = 3) -> bool:
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
				logger.info("Copied username: %s", username)


def main() -> None:
	"""
	Main entry point for the application.
	"""
	try:
		root = tk.Tk()
		UsernameGenerator(root)
		root.mainloop()
	except Exception as exc:
		logger.critical("Application failed to start", exc_info=True)
		messagebox.showerror("Critical Error", str(exc))


if __name__ == "__main__":
	main()