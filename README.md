# DSA Recall - Spaced Repetition App for Data Structures & Algorithms

A terminal-based spaced repetition application for practicing Data Structures and Algorithms problems.

## Features

- 📚 Store DSA problems with notes and code
- 🧠 Spaced repetition algorithm for optimal review scheduling
- 🔥 Streak tracking to maintain consistent practice
- 📝 External editor integration for writing detailed notes
- 🖥️ Clean terminal-based user interface
- 💾 Offline SQLite database
- 🔄 Cross-platform support (Linux, Windows, macOS)

## Installation

### From Source

1. Clone the repository:
```bash
git clone https://github.com/pranav244872/dsa-recall.git
cd dsa-recall
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

### Standalone Executable

To create a standalone executable using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile main.py
```

The executable will be created in the `dist/` directory.

## Usage

### Main Menu

Navigate using arrow keys and press Enter to select:

1. ➕ Add Problem - Add a new DSA problem
2. 📅 Review Due Problems - Review problems scheduled for today
3. 📖 View All Problems - Browse all stored problems
4. 🔥 View Streak Tracker - Check your practice streak
5. 🚪 Exit - Close the application

### Keyboard Shortcuts

- `[a]` - Toggle approach text
- `[c]` - Toggle code text
- `[e]` - Mark problem as easy (increases streak)
- `[h]` - Mark problem as hard (resets streak)
- `[E]` - Edit problem
- `[D]` - Delete problem
- `[t]` - Edit title
- `[l]` - Edit link
- `[s]` - Save changes
- `[←]` - Go back

### Spaced Repetition Algorithm

- **Easy**: Increases streak level, next review = today + 2^streak_level days
- **Hard**: Resets streak to 1, next review = tomorrow
- **Auto-Hard**: Problems overdue by more than 1 day are automatically marked as hard

## Database Location

The SQLite database is stored in:

- **Linux**: `~/.config/dsarecall/dsarecall.db`
- **Windows**: `%APPDATA%/dsarecall/dsarecall.db`
- **macOS**: `~/.config/dsarecall/dsarecall.db`

## External Editor

For writing detailed approaches and code, the app uses your system's default editor:

- Set via `$EDITOR` environment variable (e.g., `export EDITOR=vim`)
- Falls back to `nano` on Unix systems or `notepad` on Windows

## Requirements

- Python 3.7+
- textual>=0.41.0
- pyinstaller>=5.0.0 (for creating executables)

## Development

The codebase is modular and well-commented for easy expansion:

```
src/
├── database/          # SQLite models and operations
├── ui/               # Terminal UI components
│   ├── screens/      # Individual application screens
│   └── widgets/      # Reusable UI widgets
├── utils/            # Utility functions
└── config.py         # Configuration constants
```

## License

MIT License - see LICENSE file for details.
