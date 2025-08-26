# DSA Recall - Spaced Repetition App for Data Structures & Algorithms

A GUI-based spaced repetition application for practicing Data Structures and Algorithms problems.

## Features

- 📚 Store DSA problems with notes and code
- 🧠 Spaced repetition algorithm for optimal review scheduling
- 🔥 Streak tracking to maintain consistent practice
- 📝 External editor integration for writing detailed notes
- 🖥️ Clean GUI interface with card-based problem display
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

### Main Dashboard

The main dashboard shows problems due for review today in a card-based format. Navigation options include:

- **[a] Add Problem** - Add a new DSA problem
- **[b] View All Problems** - Browse all stored problems
- **[s] View Streak Tracker** - Check your practice streak
- **[q] Exit** - Close the application

### Problem Cards

Each problem card displays:
- Problem title and link
- Preview of approach and code (if set)
- Current streak level and next review date

Actions available for each problem:
- **[e1] Easy** - Mark problem as easy (increases streak)
- **[h1] Hard** - Mark problem as hard (resets streak)
- **[v1] View/Edit** - Open detailed problem view

### Keyboard Shortcuts

In problem review mode:
- `[e]` - Mark problem as easy
- `[h]` - Mark problem as hard
- `[t]` - Edit title
- `[l]` - Edit link
- `[a]` - Edit approach (external editor)
- `[c]` - Edit code (external editor)
- `[o]` - Open link in browser
- `[s]` - Save changes
- `[b]` - Go back

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
- pyinstaller>=5.0.0 (for creating executables)
- No additional GUI framework dependencies (uses built-in Python libraries)

## Development

The codebase is modular and well-commented for easy expansion:

```
src/
├── database/          # SQLite models and operations
├── gui/               # GUI components and windows
│   └── windows/       # Individual application windows
├── utils/             # Utility functions
└── config.py          # Configuration constants
```

## License

MIT License - see LICENSE file for details.
