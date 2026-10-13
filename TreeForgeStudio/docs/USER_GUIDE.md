# TreeForge Studio - User Guide

> **Note**: This user guide provides detailed step-by-step instructions for using TreeForge Studio. For a quick overview of features, see the [README.md](../README.md).

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Page Walkthrough](#dashboard-page-walkthrough)
3. [Creating Project Structures](#creating-project-structures)
4. [File Editing Workflows](#file-editing-workflows)
5. [Batch Operations](#batch-operations)
6. [Advanced Features](#advanced-features)
7. [Customization & Settings](#customization--settings)
8. [Tips & Best Practices](#tips--best-practices)
9. [Troubleshooting FAQ](#troubleshooting-faq)

---

## Getting Started

### Launching the Application

From the project root directory:
```bash
# Activate virtual environment (if not already activated)
source .venv/bin/activate  # Linux/macOS
# .\.venv\Scripts\activate  # Windows PowerShell

# Launch
python main.py
```

### First-Time Setup

On first launch, you'll see:
1. **Dashboard page** (default landing page)
2. **Toolbar** at the top (language/theme selectors, accent color)
3. **Sidebar** with navigation buttons (Dashboard, Project Explorer, Batch Editor, etc.)
4. **Status bar** at the bottom showing current language/theme

---

## Dashboard Page Walkthrough

The Dashboard is where you create project structures from text descriptions.

### Main Components

1. **Left Panel** - Tree Input Area
   - Large text area for entering directory trees
   - Buttons: Load Example, Parse Tree, Clear

2. **Right Panel** - Preview Area
   - Interactive tree preview with icons
   - Context menu for marking ambiguous entries
   - Conflict policy selector (Skip/Backup/Stop)
   - Destination selection (Browse or manual entry)
   - Create Structure button

3. **Bottom Panel** - Action Log
   - Shows parse results, creation progress, and errors

### Supported Tree Formats

#### Basic Notation
```text
MyProject/
├── main.py
├── README.md
├── assets/
│   └── logo.png
└── tests/
    └── test_main.py
```

#### Compact Declarations
```text
ui/ (main_window.py, styles.py, spinner.py)
core/ (engine.py, utils.py)
services/ (api.py, db.py)
```

#### Mixed Formats
```text
Project/
├── src/
│   ├── main.py
│   └── utils/ (helpers.py, constants.py)
├── tests/ (test_main.py, test_utils.py)
├── .gitignore
└── README.md
```

### Parsing Process

1. **Enter your tree** in the left text area
2. **Click "Parse Tree"** - the app analyzes and shows a preview
3. **Review ambiguous entries** (shown in yellow):
   - Right-click → "Mark as File" or "Mark as Directory"
4. **Select destination folder** using "Browse" or manual path entry
5. **Choose conflict policy**:
   - **Skip existing files** (default) - safest, never overwrites
   - **Backup and overwrite** - saves *.bak* copies first
   - **Stop on conflict** - aborts if any file exists
6. **Click "Create Structure"** - watch the progress dialog

---

## Creating Project Structures

### Step-by-Step Example

Let's create a simple web project:

1. **Enter this tree** in the Dashboard:
```text
MyWebsite/
├── index.html
├── css/
│   ├── styles.css
│   └── responsive.css
├── js/
│   ├── main.js
│   └── utils.js
├── assets/
│   ├── images/ (logo.png, banner.jpg)
│   └── icons/ (favicon.ico)
└── README.md
```

2. **Click "Parse Tree"** - preview appears on right
3. **Verify all items** are correctly classified:
   - Folders should have folder icons
   - Files should have document icons
   - Yellow items need manual classification

4. **Set destination**: Click "Browse" and choose where to create the project
5. **Keep default policy**: "Skip existing files"
6. **Click "Create Structure"**
7. **Review progress dialog** showing files being created
8. **Click "Finish"** when complete

### Result
Your destination now contains:
```
/path/to/destination/MyWebsite/
├── index.html
├── css/
│   ├── styles.css
│   └── responsive.css
├── js/
│   ├── main.js
│   └── utils.js
├── assets/
│   ├── images/
│   │   ├── logo.png
│   │   └── banner.jpg
│   └── icons/
│       └── favicon.ico
└── README.md
```

---

## File Editing Workflows

### Opening Files in Editor

1. Go to **Project Explorer** page (sidebar button)
2. Navigate your created project structure
3. **Double-click any file** to open it in the editor
4. Or right-click → "Open in Editor"

### Using the Text Editor

The editor supports:
- **UTF-8 text** (English, Arabic, emoji, code)
- **Standard shortcuts**:
  - `Ctrl+Z` / `Ctrl+Y` - Undo/Redo
  - `Ctrl+C` / `Ctrl+V` / `Ctrl+X` - Copy/Paste/Cut
  - `Ctrl+F` - Find & Replace
  - `Ctrl+S` - Save
  - `Ctrl+Shift+S` - Save As

#### Find & Replace Features

1. Press `Ctrl+F` or click the magnifying glass icon
2. Enter search term in "Find" field
3. Optional: Enter replacement in "Replace with" field
4. Toggle options:
   - **Aa** - Case sensitive
   - **\*b** - Whole words only
   - **.*** - Regular expression (advanced)
5. Actions:
   - **Find Next** (`Enter`) - Jump to next match
   - **Replace** - Replace current match
   - **Replace All** - Replace all matches in document
   - **Clear** - Clear search

#### Dirty State Indicators

- Unchanged document: Clean tab title
- Modified document: Tab title shows `*` prefix
- Saved document: Returns to clean state

---

## Batch Operations

### Mode A: Apply Same Text to Multiple Files

Useful for adding headers, licenses, or boilerplate.

#### Workflow
1. In **Project Explorer**, select multiple files:
   - `Ctrl+Click` for individual selection
   - `Shift+Click` for range selection
   - Click folder to select all files within
2. Click **Batch Editor** in sidebar
3. Choose **Write Mode**:
   - **Replace** - Overwrite entire file content
   - **Append** - Add to end of existing content
   - **Prepend** - Add to beginning of existing content
4. Enter your text in the input area
5. Click **Apply to Selected Files**
6. **Review confirmation dialog** showing affected files
7. Click **Confirm** to proceed

#### Example: Adding License Headers
1. Select all source files (.py, .js, .html)
2. Choose **Prepend** mode
3. Enter:
```text
# Copyright 2026 Your Name
# Licensed under MIT License
#
```
4. Apply - adds header to beginning of each selected file

### Mode B: Multi-File Editor (Independent Content)

Each file gets its own tab with independent editing.

#### Workflow
1. Select multiple files in Project Explorer
2. Right-click → **Open in Multi-File Editor**
   - Or click **Multi-File Editor** in sidebar when files are selected
3. Each file opens as a tab showing:
   - File name and path
   - Independent editor content
   - Unsaved indicator (`*`)
   - Close button (`x`)
4. Edit each tab independently
5. Click **Save All** to write all modified files
6. Individual results shown in status bar per file

#### Advantages Over Mode A
- Different content per file
- Real-time editing with instant feedback
- Better for complex edits requiring file-specific changes

---

## Advanced Features

### Advanced Batch Content Format

Paste multiple files with contents in one go using delimiters.

#### Format
```text
=== FILE: path/to/file1.ext ===
Content of file 1...

=== FILE: path/to/file2.ext ===
Content of file 2...

=== FILE: another/dir/file3.ext ===
Content of file 3...
```

#### Rules
- Each block starts with `=== FILE: <relative/path> ===` on its own line
- Content continues until next marker or end
- Multiline content supported
- Nested paths allowed (e.g. `src/components/Button.jsx`)
- **Safety checks**: Absolute paths, `../` traversal, drive letters, null bytes rejected

#### Workflow
1. Go to **Batch Content Format** page (sidebar)
2. Paste content using the format above
3. Click **Parse Batch Content** to preview detected files
4. Review file list and content previews
5. Click **Apply to Files**
6. Confirm in the dialog that appears
7. Results shown per file

#### Example: Creating a Web Page Bundle
```text
=== FILE: index.html ===
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Site</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <h1>Welcome</h1>
    <p>This is my website.</p>
    <script src="js/main.js"></script>
</body>
</html>

=== FILE: css/styles.css ===
body {
    font-family: sans-serif;
    margin: 40px;
    line-height: 1.6;
}

h1 {
    color: #2c3e50;
}

=== FILE: js/main.js ===
document.addEventListener('DOMContentLoaded', function() {
    console.log('Site loaded!');
    
    const heading = document.querySelector('h1');
    heading.addEventListener('click', function() {
        alert('Hello from JavaScript!');
    });
});
```

---

## Customization & Settings

### Theme & Language Switching

Located in the toolbar (top-right area):

#### Language Selector
- **English** - Left-to-right layout
- **العربية** - Right-to-left layout for menus/dialogs
  - Code and file paths remain left-to-right
  - Instant switch, no restart needed

#### Theme Selector
- **Light** - Light background, dark text
- **Dark** - Dark background, light text  
- **System** - Follows OS theme preference

#### Accent Color Button
- Cycles through predefined accent colors
- Affects highlights, buttons, selection colors
- Persisted with theme setting

### Persistent Settings

All preferences automatically saved:
- Language and theme
- Window size and position
- Last used destination folder
- Recent projects list
- Editor preferences (font, size, tab width)
- Batch operation preferences

#### Manual Settings Access
Some advanced settings available via:
1. **Settings** button in toolbar (gear icon)
2. Or right-click in Project Explorer → Settings

Available sections:
- **General**: Startup behavior, confirmation dialogs
- **Editor**: Font family, size, tab width, wrap settings
- **Batch Operations**: Default write mode, confirmation preferences
- **File Service**: Backup settings, atomic write options
- **About**: Version, dependencies, license info

#### Reset Options
- **Restore Default Settings** - Resets all preferences to factory defaults
- **Clear Recent Projects** - Clears the recent projects list
- **Export/Import Settings** - Save/load settings as JSON file

---

## Tips & Best Practices

### Efficient Project Creation

1. **Start with examples**: Use "Load Example" to see supported formats
2. **Use compact notation**: `folder/ (file1.py, file2.py)` saves typing
3. **Validate before creating**: Always review the preview after parsing
4. **Choose safe defaults**: Stick with "Skip existing files" unless you intend to overwrite
5. **Use descriptive names**: Clear folder/file names improve maintainability

### Editing Best Practices

1. **Save frequently**: Use `Ctrl+S` or enable auto-save in settings
2. **Use Multi-File Editor** for complex multi-file changes
3. **Leverage Find & Replace**:
   - Whole-word mode prevents partial matches
   - Case-sensitive when needed for code refactoring
   - Preview replacements before applying "Replace All"
4. **Monitor dirty state**: The `*` indicator prevents accidental loss of work

### Batch Operation Safety

1. **Always review confirmations**: The app shows exactly what will be affected
2. **Start with small tests**: Try on 1-2 files before large batch operations
3. **Use backups**: Enable "Backup and overwrite" when experimenting
4. **Check results**: Review the status bar for per-file success/failure reports

### Performance Tips

1. **Large projects**: Creation progress dialog shows real-time progress
2. **Network drives**: May be slower; consider local development then copy
3. **Antivirus software**: May slow file creation; add exclusion for dev folders
4. **Very large files**: Editor handles large files but consider external tools for GB-sized logs/data

---

## Troubleshooting FAQ

### Startup Issues

**Q: Application fails to start with "Qt platform plugin not found"**  
A: Install required system dependencies:
```bash
# Ubuntu/Debian
sudo apt-get install libgl1 libegl1 libxkbcommon0 \
    libxcb-cursor0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
    libxcb-shape0 libxcb-xinerama0 libdbus-1-3 libfontconfig1

# Fedora
sudo dnf install python3-devel qt6-qtbase gui-libs
```

**Q: Application starts but shows blank window**  
A: Try setting the Qt platform explicitly:
```bash
QT_QPA_PLATFORM=xcb python main.py
```

### Arabic Text Issues

**Q: Arabic text appears as disconnected letters or boxes**  
A: Install an Arabic-capable font:
```bash
# Ubuntu/Debian
sudo apt-get install fonts-noto-core fonts-noto-core-extra

# Or download Cairo/Noto fonts manually
```
Then go to Settings → Editor → Font Family and select the Arabic font.

### File Operation Issues

**Q: Files not saved or changes lost**  
A: Check:
1. Conflict policy - "Skip existing files" prevents overwrites
2. Write permissions - try a different destination folder
3. Disk space - ensure sufficient space on target drive
4. File locks - ensure no other process has the file open

**Q: "Access denied" or permission errors**  
A: 
- Run with appropriate user permissions
- Avoid system-protected folders (use Documents/, Projects/, etc.)
- On Linux, check folder permissions with `ls -ld /path/to/folder`

### Batch Operation Issues

**Q: Batch operation affects wrong files**  
A: 
- Double-check selection in Project Explorer before batch operations
- Remember: Selecting a folder selects ALL files within it
- Use Ctrl+Click to deselect specific files if needed

**Q: Advanced batch format not parsing**  
A: 
- Verify delimiter format exactly: `=== FILE: path/to/file ===`
- Ensure no extra spaces before/after the delimiter
- Check that paths are relative (no leading `/` or drive letters)
- Validate no forbidden patterns (`..`, `:`, `\0`)

### Performance Issues

**Q: Application feels slow during large project creation**  
A: Normal for thousands of files; progress dialog shows throughput. Consider:
- Creating in batches for extremely large projects
- Using SSD storage for better performance
- Closing other applications to free system resources

**Q: Editor lag with very large files**  
A: 
- The editor is optimized for typical source files (KB to low MB)
- For multi-MB log files, consider external tools like `less`, `vim`, or specialized log viewers
- Enable "Word wrap" in settings only if needed (can affect performance with very long lines)

### Settings & Configuration

**Q: Settings not persisting between launches**  
A: 
- Ensure you have write permissions to the application directory
- Check that `.ini` or registry settings can be created (Qt QSettings)
- Try launching with explicit permissions if using sudo/unusual setup

**Q: Want to reset to original state**  
A: Use Settings → Restore Default Settings, or delete the QSettings location:
- Windows: Registry under `HKEY_CURRENT_USER\Software\TreeForgeStudio`
- Linux: `~/.config/TreeForgeStudio.conf`
- macOS: `~/Library/Preferences/TreeForgeStudio.plist`

---

## Keyboard Shortcuts Reference

### Global Shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl+Q` | Quit application |
| `Ctrl+,` | Open Settings dialog |
| `F1` | Show this help (if implemented) |

### Dashboard Page
| Shortcut | Action |
|----------|--------|
| `Ctrl+L` | Load Example tree |
| `Ctrl+P` | Parse Tree |
| `Ctrl+Enter` | Create Structure (when preview ready) |
| `Ctrl+Backspace` | Clear tree input |

### Text Editor
| Shortcut | Action |
|----------|--------|
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+C` | Copy |
| `Ctrl+V` | Paste |
| `Ctrl+X` | Cut |
| `Ctrl+F` | Open Find & Replace |
| `Ctrl+H` | Open Find & Replace (focus replace field) |
| `Ctrl+G` | Go to Line |
| `Ctrl+S` | Save |
| `Ctrl+Shift+S` | Save As |
| `Ctrl+A` | Select All |
| `Ctrl+[` | Decrease Indent |
| `Ctrl+]` | Increase Indent |
| `Tab` | Insert tab (or indent if text selected) |
| `Shift+Tab` | Decrease Indent |

### Find & Replace Panel
| Shortcut | Action |
|----------|--------|
| `Enter` | Find Next |
| `Shift+Enter` | Find Previous |
| `Ctrl+Enter` | Replace All |
| `Alt+Enter` | Replace & Find Next |
| `Esc` | Close panel |

### Project Explorer
| Shortcut | Action |
|----------|--------|
| `F2` | Rename selected item |
| `Del` | Delete selected item(s) |
| `Ctrl+A` | Select all visible items |
| `Ctrl+F` | Focus search/filter box |
| `Ctrl+Shift+F` | Clear search/filter |

### Multi-File Editor
| Shortcut | Action |
|----------|--------|
| `Ctrl+Tab` | Next tab |
| `Ctrl+Shift+Tab` | Previous tab |
| `Ctrl+W` | Close current tab |
| `Ctrl+Shift+W` | Close all tabs |
| `Ctrl+Shift+S` | Save All |

---

## Conclusion

TreeForge Studio provides a powerful, safe workflow for turning textual directory descriptions into real project structures and efficiently editing the resulting files. By combining intuitive tree parsing with professional editing capabilities and robust batch operations, it streamlines project setup and maintenance tasks.

For additional information:
- See [README.md](../README.md) for feature overview and technical details
- Check the [source code](./../app/) for implementation specifics
- Refer to the troubleshooting section above for common issues

Happy coding! 🚀