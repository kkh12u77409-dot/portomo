# TreeForge Studio — User Guide

This guide explains every part of the interface and the recommended workflows.

---

## 1. The Interface

The window is split into three main regions:

- **Toolbar (top)** — application name, New / Open / Save / Save All, the
  language and theme selectors, Refresh, Settings, About, and the accent-color
  button.
- **Sidebar (left)** — navigation between five pages:
  - **Dashboard** — paste and parse a tree, choose a destination, preview, and
    create the structure.
  - **Project Explorer** — browse the project and edit a single file.
  - **Batch Editor** — Mode A (same text to many files) and the batch content
    format.
  - **Multi-File Editor** — Mode B (different content per file).
  - **Settings** — language, theme, editor, filesystem, and recent projects.
- **Content area (center/right)** — the active page, with resizable split
  panels.

---

## 2. Parsing a Tree

### Input locations
Everything starts on the **Dashboard** page in the *Directory Tree* text area.

### Supported notations

| Notation | Example | Meaning |
| --- | --- | --- |
| Unicode branch | `├── main.py` | a child entry |
| Unicode last branch | `└── README.md` | the final sibling |
| Continuation bar | `│` | indicates deeper siblings follow |
| Trailing slash | `src/` | a directory |
| Compact declaration | `ui/ (a.py, b.py)` | a folder with comma-separated children |
| Nested path | `assets/icons/` | directory inside directory |
| Dotfile | `.gitignore` | a file beginning with a dot |
| Extensionless | `Makefile` | ambiguous — flagged for review |

### Parsing workflow
1. Paste the tree.
2. Click **Parse Tree**.
3. Review errors and warnings (each with a line number).
4. Fix *ambiguous* entries in the preview using the right-click context menu:
   - **Mark as File**
   - **Mark as Directory**
5. Only when validation succeeds does **Create Structure** become enabled.

### Ambiguous entries
A name without a trailing slash and without an extension (for example
`Makefile` or `LICENSE`) cannot be confidently classified, so it is flagged as
*ambiguous* and marked with `[?]` in the preview. Correct its type before
creating the structure.

---

## 3. Choosing a Destination

The destination control contains:

- A **text field** showing the current destination.
- A **Browse** button that opens the native directory dialog.
- A **root indicator** showing exactly what will be created, for example
  `D:\PythonProjects\SumMaster`.

You may type any path manually. The app validates that the destination is
usable and that the created root does not escape it. You can change the
destination at any time before creation without re-entering the tree.

---

## 4. Conflict Policy

Choose the behaviour when a target file already exists:

| Policy | Behaviour | Default |
| --- | --- | --- |
| **Skip existing files** | Preserve all existing files, create only the missing ones | ✅ Yes |
| **Backup and overwrite** | Copy existing files to `*.bak`, then overwrite | No |
| **Stop on conflict** | Report the conflict and do not overwrite | No |

The safest option is selected by default and existing files are never
overwritten silently.

---

## 5. Project Explorer

The explorer mirrors the parsed tree and the real filesystem.

- **Expand / collapse** folders with the arrows or double-click.
- **Select** a file to open it in the editor.
- **Multi-select** with `Ctrl`/`Shift` for batch operations.
- **Search / filter** using the search box above the tree.
- **Context menu**: Open in Editor, Open in Multi-File Editor, Expand All,
  Collapse All, Refresh.
- The **relative path** of the selected file is shown above the editor.
- **Refresh** re-syncs the tree with the filesystem after external changes.

Selecting a folder for a batch operation includes all of its descendant files.

---

## 6. Single-File Editor

- Opens the selected file's content in UTF-8.
- Supports multiline text, Arabic, English, emoji, and source code.
- Standard editing: copy, cut, paste, select all, undo, redo.
- **Find & Replace** (`Ctrl+F`): case-sensitive, whole-word, previous/next,
  replace, and replace all.
- **Save** (`Ctrl+S`) writes atomically; **Save As** writes a copy.
- Unsaved changes are marked with `*` next to the file name.
- The status bar shows the cursor **line and column**.

### Binary files
Files that look binary (PNG, JPEG, archives, compiled artifacts) are not loaded
into the editor. The app shows a warning and requires an explicit override.

---

## 7. Batch Editor — Mode A (same text)

1. Select files in the explorer.
2. Choose the **Write Mode**: Replace, Append, or Prepend.
3. Type the text.
4. Click **Apply to Selected Files**.

Before overwriting existing content the app lists the affected files and asks
for confirmation. On completion it reports successful, skipped, and failed
writes. Files that look binary trigger a warning.

---

## 8. Multi-File Editor — Mode B (different content per file)

1. Select multiple files and choose **Open in Multi-File Editor**.
2. Each file opens as its own tab, each with an independent editor and
   unsaved indicator (a `●` prefix on the tab).
3. Edit freely, then click **Save All**.

Each file is written to its own destination, and every result (success or
failure) is reported individually. Closing a tab with unsaved changes prompts
you to save, discard, or cancel.

---

## 9. Advanced Batch Content Format

Use this when you want to define the content for several files at once.

1. Open the **Batch Editor** page, right pane.
2. Paste content in this form:

   ```text
   === FILE: main.py ===
   print("Hello from TreeForge Studio")

   === FILE: README.md ===
   # My Project

   Project documentation goes here.

   === FILE: requirements.txt ===
   PyQt6
   ```

3. Click **Parse Batch Content** to preview the detected target files.
4. Click **Apply to Files** and confirm.

Rules:

- Each block starts with `=== FILE: <path> ===` on its own line.
- Content is everything up to the next marker (or end of input).
- Multiline content is preserved.
- Nested relative paths are allowed.
- Absolute paths, `../` traversal, drive prefixes, and null bytes are rejected.
- Nothing is written without explicit confirmation.

---

## 10. Settings

- **General**: language, theme, sidebar visibility.
- **Editor**: font family, font size, auto indent.
- **Filesystem**: show hidden files, conflict policy, create backups before
  replace.
- **Recent Projects**: list, refresh, and clear.

**Restore Default Settings** resets every preference to its default value.

---

## 11. Keyboard Shortcuts

| Action | Shortcut |
| --- | --- |
| Find & Replace | `Ctrl+F` |
| Save current file | `Ctrl+S` |
| Save all open files | `Ctrl+Shift+S` |
| Close window | `Ctrl+Q` |

---

## 12. Where Preferences Are Stored

Preferences use `QSettings`:

- **Windows**: registry under `HKEY_CURRENT_USER\Software\TreeForgeStudio`.
- **Linux**: `~/.config/TreeForgeStudio/TreeForgeStudio.ini` (or the Qt
  equivalent for your desktop).

Stored values include language, theme, window size and position, last
destination, recent projects, and editor/batch preferences. No passwords or
credentials are ever stored.

---

## 13. Tips

- Click **Load Example** on the Dashboard to see the full feature set in one
  click.
- Use the **Accent** button in the toolbar to personalize the current theme.
- Switching to Arabic instantly flips the layout to right-to-left while keeping
  code and file paths left-to-right.
- Batch previews always name the affected files so you never write blindly.
