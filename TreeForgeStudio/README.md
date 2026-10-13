# TreeForge Studio

**TreeForge Studio** is a professional bilingual (English / العربية) desktop
application that turns plain-text directory trees into real project
structures and provides a powerful, safe multi-file content editing workflow.

Built with **Python 3.10+** and **PyQt6 (Qt Widgets)**.

---

## Table of Contents

1. [Features](#features)
2. [Screenshots](#screenshots)
3. [Project Structure](#project-structure)
4. [Supported Platforms](#supported-platforms)
5. [Requirements](#requirements)
6. [Installation](#installation)
7. [Launching the Application](#launching-the-application)
8. [Entering a Directory Tree](#entering-a-directory-tree)
9. [Creating a Project Structure](#creating-a-project-structure)
10. [Editing Individual Files](#editing-individual-files)
11. [Saving Content to Multiple Files](#saving-content-to-multiple-files)
12. [Advanced Batch Content Format](#advanced-batch-content-format)
13. [Switching Themes and Languages](#switching-themes-and-languages)
14. [Troubleshooting](#troubleshooting)
15. [Running Automated Tests](#running-automated-tests)
16. [Building a Standalone Executable](#building-a-standalone-executable)
17. [Security Notes](#security-notes)
18. [License](#license)

---

## Features

- **Tree parsing** from plain text using Unicode tree characters
  (`├──`, `└──`, `│`), indentation, trailing-slash folders, dotfiles,
  extensionless files, and compact declarations with comma-separated
  children in parentheses (`ui/ (main_window.py, spinner.py)`).
- **Live preview** of the parsed tree with the ability to correct file /
  directory classification for ambiguous entries.
- **Destination selection** with a native folder browser, manual entry,
  validation, and clear indication of the root directory that will be created.
- **Structure creation** including nested directories and empty folders, with
  a real progress dialog, a creation summary, and a configurable conflict
  policy (skip / backup / error).
- **Interactive project explorer** with expand/collapse, file & folder icons,
  multi-selection, search filtering, context menus, relative paths, and
  filesystem refresh.
- **Professional text editor** supporting multiline UTF-8 text (Arabic,
  English, emoji, code), copy/cut/paste/undo/redo, find & replace, dirty-state
  indicators, Save / Save As, and confirmation before discarding changes.
- **Batch editing — Mode A**: apply the same text to many files using
  *Replace*, *Append*, or *Prepend*, with confirmation before destructive
  operations.
- **Batch editing — Mode B**: a dedicated multi-file tabbed editor where each
  file keeps its own independent content, unsaved indicator, and **Save All**.
- **Advanced batch content format**: paste multiple file paths with their
  contents in one area, preview the parsed targets, and write them after
  confirmation.
- **Safe file service**: UTF-8 by default, atomic writes via temporary files,
  optional backups, read-only and binary detection, per-file result tracking,
  and honest partial-failure reporting.
- **Full Arabic / English localization** with runtime switching, right-to-left
  layout for Arabic, and left-to-right preserved for paths and code.
- **Light and dark themes** applied instantly via Qt Style Sheets (QSS), with a
  consistent accent color, refined typography, rounded panels, styled
  scrollbars, tooltips, menus, dialogs, tabs, and progress indicators.
- **Persistent settings** (language, theme, window geometry, last destination,
  recent projects, editor and batch-operation preferences) using `QSettings`.
- **Background workers** (`QThread`) for filesystem tasks so the UI never
  blocks.
- **SVG icon set** rendered and recolored at runtime — no binary image assets.

---

## Screenshots

Screenshots are not bundled to keep the repository text-only. Capture your own:

1. Launch the application (`python main.py`).
2. Click **Load Example**, then **Parse Tree**.
3. Choose a destination and click **Create Structure**.
4. Open a file in the editor and switch to the **Multi-File Editor**.
5. Use the toolbar **language** and **theme** selectors to capture the
   Arabic right-to-left layout and the light theme.

Recommended tools to capture screenshots:

- **Windows**: `Win + Shift + S` (Snip & Sketch) or `PrtScn`.
- **Linux (GNOME)**: `PrtScn` or `gnome-screenshot -a`.
- **Linux (KDE)**: `Spectacle`.

---

## Project Structure

```text
TreeForgeStudio/
├── main.py                     # Application entry point
├── requirements.txt            # Pinned runtime + test dependencies
├── README.md                   # This file
├── app/
│   ├── __init__.py
│   ├── main_window.py          # Main window, toolbar, sidebar, pages
│   ├── tree_parser.py          # Plain-text tree parser + model
│   ├── project_service.py      # Directory/file creation + conflict policy
│   ├── file_content_service.py # Safe read/write, backups, batch content
│   ├── settings_service.py     # QSettings persistence
│   ├── theme_manager.py        # Light/dark themes + QSS generation
│   ├── translations.py         # Centralized Arabic/English strings
│   ├── icons.py                # Runtime SVG icon rendering
│   └── widgets/
│       ├── __init__.py
│       ├── project_explorer.py # Interactive file/folder tree
│       ├── text_editor.py      # Single-file editor + find/replace
│       ├── multi_file_editor.py# Multi-file tabbed editor (Save All)
│       └── progress_dialog.py  # QThread progress dialog
├── assets/
│   └── icons/
│       └── app_icon.svg        # Application icon asset
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Shared fixtures + QSettings isolation
│   ├── test_tree_parser.py
│   ├── test_project_service.py
│   ├── test_file_content_service.py
│   ├── test_settings.py
│   └── test_translations.py
└── docs/
    └── USER_GUIDE.md           # Detailed usage guide
```

---

## Supported Platforms

- **Windows 10 / 11**
- **Mainstream Linux distributions** (Ubuntu, Debian, Fedora, Arch, openSUSE)

The application uses `pathlib` for portable, safe filesystem operations and
does not require an internet connection for normal functionality.

---

## Requirements

- Python **3.10** or newer
- PyQt6 **6.6.0** or newer
- pytest **7.4.0** or newer (tests only)

All runtime dependencies are listed in `requirements.txt`:

```text
PyQt6>=6.6.0
pytest>=7.4.0
```

---

## Installation

### Windows (PowerShell)

```powershell
# From the project root (the folder containing main.py)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

If PowerShell blocks activation scripts, run once as your user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Linux (bash)

```bash
# From the project root
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

#### Linux system dependencies

PyQt6 requires a few shared libraries. On Debian/Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip \
    libgl1 libegl1 libxkbcommon0 \
    libxcb-cursor0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
    libxcb-shape0 libxcb-xinerama0 libdbus-1-3 libfontconfig1
```

On Fedora:

```bash
sudo dnf install python3-devel qt6-qtbase gui-libs
```

---

## Launching the Application

```bash
python main.py
```

On launch the persisted language and theme are applied before the first
paint, and the last destination is restored.

---

## Entering a Directory Tree

Open the **Dashboard** page and paste your tree into the left-hand text area.
The app recognises common notations:

```text
SumMaster/
├── main.py
├── make_zip.py
├── requirements.txt
├── README.md
├── assets/icons/
├── ui/ (main_window.py, spinner.py, styles.py)
├── core/ (calculator.py, worker.py)
├── services/ (settings_service.py)
└── tests/ (test_calculator.py, test_worker.py)
```

Supported formats:

- Unicode tree characters: `├──`, `└──`, `│`
- Plain indentation (spaces or tabs)
- Nested paths, e.g. `assets/icons/`
- Directories identified by a trailing `/`
- Compact folder declarations with comma-separated children in parentheses,
  e.g. `ui/ (main_window.py, styles.py)` — expanded into proper nested nodes
- Dotfiles (`.gitignore`, `.env`) and extensionless files
- Empty directories and blank lines

Click **Load Example** to fill the sample tree, then **Parse Tree**.

---

## Creating a Project Structure

1. On the **Dashboard**, pick a destination with **Browse** or type it
   manually (e.g. `D:\PythonProjects` or `/home/user/PythonProjects`).
2. Click **Parse Tree** and inspect the preview. Fix any *ambiguous* entries
   with the preview context menu (**Mark as File** / **Mark as Directory**).
3. Choose a **conflict policy**:
   - **Skip existing files** *(default, safest)* — never overwrites.
   - **Backup and overwrite** — copies existing files to `*.bak` first.
   - **Stop on conflict** — treats an existing file as an error.
4. Click **Create Structure**, confirm the summary, and watch the progress
   dialog.

Creating the example under a destination `D:\PythonProjects` produces:

```text
D:\PythonProjects\SumMaster\
├── main.py
├── make_zip.py
├── requirements.txt
├── README.md
├── assets/
│   └── icons/
├── ui/
│   ├── main_window.py
│   ├── spinner.py
│   └── styles.py
├── core/
│   ├── calculator.py
│   └── worker.py
├── services/
│   └── settings_service.py
└── tests/
    ├── test_calculator.py
    └── test_worker.py
```

The root folder is created exactly once — the app never duplicates it based on
the destination you typed.

---

## Editing Individual Files

1. Go to **Project Explorer**.
2. Double-click a file (or use the context menu **Open in Editor**).
3. Edit the content. Arabic, English, emoji, Unicode, and source code are all
   supported in UTF-8.
4. Use **Find & Replace** (`Ctrl+F`) for search and replacement.
5. Press **Save** (`Ctrl+S`) or **Save As**. Unsaved changes are marked with a
   `*` and the app warns you before discarding them.

Binary-looking files (PNG, JPEG, archives, compiled binaries) are detected and
blocked from arbitrary text editing unless you explicitly override.

---

## Saving Content to Multiple Files

### Mode A — Apply the same text to several files

1. Select files in the **Project Explorer** (Ctrl/Shift-click for
   multi-selection, or select a folder to include all its files).
2. Open **Batch Editor**.
3. Enter the text and pick the **Write Mode**:
   - **Replace** — overwrite the whole content.
   - **Append** — add to the end.
   - **Prepend** — add to the beginning.
4. Click **Apply to Selected Files**.

Before overwriting existing content the app shows a confirmation listing the
affected files. A final summary reports successful, skipped, and failed writes.

### Mode B — Give each file its own content

1. Select multiple files and use **Open in Multi-File Editor**.
2. Each file opens as its own tab with an independent editor and unsaved
   indicator.
3. Edit each tab, then click **Save All**.

Each file is written to its correct destination and every result is reported
individually — partial failures are never hidden.

---

## Advanced Batch Content Format

Paste several file paths and their contents into a single area using the
`=== FILE: path ===` delimiter syntax:

```text
=== FILE: main.py ===
print("Hello from TreeForge Studio")

=== FILE: README.md ===
# My Project

Project documentation goes here.

=== FILE: requirements.txt ===
PyQt6
```

1. Paste into the **Batch Content Format** pane.
2. Click **Parse Batch Content** to preview the detected target files.
3. Click **Apply to Files** and confirm.

Delimiter rules:

- Each file block starts with `=== FILE: <relative/path> ===` on its own line.
- Content continues until the next `=== FILE: ===` marker or the end of input.
- Multiline content is fully supported.
- Nested relative paths are allowed (e.g. `src/utils/helper.py`).
- **Unsafe paths are rejected**: absolute paths, `../` traversal, Windows
  drive prefixes (`C:/`), and null bytes are refused before any write.
- Nothing is written until you explicitly confirm.

---

## Switching Themes and Languages

Use the toolbar selectors at any time — no restart is required:

- **Language selector** — English or العربية. Arabic switches the whole UI to
  right-to-left layout; code and filesystem paths stay left-to-right.
- **Theme selector** — Light, Dark, or System.

Your choice is persisted and restored on the next launch. The **Accent**
button cycles the accent color used across the current theme.

---

## Troubleshooting

**The application fails to start with a Qt platform plugin error (Linux).**
Install the system libraries listed under
[Linux system dependencies](#linux-system-dependencies) and run inside the
virtual environment.

**Arabic text renders as boxes or disconnected letters.**
Install an Arabic-capable font such as **Noto Naskh Arabic** or **Cairo** and
select it under **Settings → Editor → Font Family**.

**Changes are not saved.**
Check the **conflict policy**: with *Skip existing files* the app will not
overwrite existing content. Switch to *Backup and overwrite* if you intend to
replace files, or use the editor **Save** button which always writes the file
you are editing.

**Read-only or permission errors.**
The file service reports per-file failures in the batch summary instead of
claiming success. Run with appropriate permissions or change the target
destination.

**Settings feel stale after an update.**
Use **Settings → Restore Default Settings** to reset all preferences.

---

## Running Automated Tests

The test suite runs independently of the GUI startup:

```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
python -m pytest tests/ -v

# Linux
source .venv/bin/activate
python -m pytest tests/ -v
```

Run a single module:

```bash
python -m pytest tests/test_tree_parser.py -v
```

The suite covers parser correctness, compact expansion, nested directories,
dotfiles, ambiguous detection, unsafe-path rejection, structure creation,
empty folders, pre-existing file preservation, Arabic/English/emoji/multiline
writes, replace/append/prepend, multi-file save, partial-failure reporting, and
theme/language persistence.

> Permission-sensitive tests are skipped automatically when the suite runs as
> root, because root bypasses filesystem permission bits.

---

## Building a Standalone Executable

TreeForge Studio can be packaged with **PyInstaller**. From the project root
inside the virtual environment:

```bash
python -m pip install pyinstaller
```

Windows (one-folder build with the SVG asset):

```powershell
pyinstaller --noconfirm --windowed --name TreeForgeStudio ^
  --add-data "assets;assets" main.py
```

Linux (one-folder build):

```bash
pyinstaller --noconfirm --windowed --name TreeForgeStudio \
  --add-data "assets:assets" main.py
```

The executable is produced under `dist/`. Use `--onefile` if you prefer a
single-file build (slower startup):

```bash
pyinstaller --noconfirm --onefile --windowed --name TreeForgeStudio \
  --add-data "assets:assets" main.py
```

---

## Security Notes

- The parser **never** evaluates or executes user-provided content.
- Unsafe paths — absolute paths, `../` traversal, Windows drive prefixes, and
  null bytes — are rejected during parsing and again before any write.
- All writes are confined to the selected destination using `pathlib`
  resolution checks.
- Files are written atomically via a temporary file and `os.replace`.
- The app never deletes unrelated files or directories.

---

## License

Released for personal and commercial use. Include attribution when
redistributing.
