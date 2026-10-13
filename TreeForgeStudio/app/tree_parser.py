"""Directory-tree parser for TreeForge Studio.

Parses plain-text directory tree representations into a structured model.
Supports:
  * Unicode tree characters (``├──``, ``└──``, ``│``)
  * Indented folder/file lists
  * Nested paths (e.g. ``assets/icons/``)
  * Trailing-slash directories
  * Compact declarations with comma-separated children in parentheses
    (e.g. ``ui/ (main_window.py, spinner.py)``)
  * Dotfiles and extensionless files
  * Empty directories

The parser never evaluates or executes user content.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator, Optional


class NodeKind(Enum):
    """Classification of a parsed node."""

    DIRECTORY = "directory"
    FILE = "file"
    AMBIGUOUS = "ambiguous"


@dataclass
class TreeNode:
    """A single node in a parsed directory tree.

    ``name`` is the entry name (without path separators).
    ``kind`` is the current classification.
    ``children`` holds sub-directories.
    ``files`` holds leaf file nodes.
    ``parent`` is the owning directory or ``None`` for the root.
    ``line_number`` records where the entry was first seen.
    ``source`` is the original text for this entry.
    """

    name: str
    kind: NodeKind = NodeKind.AMBIGUOUS
    children: dict[str, "TreeNode"] = field(default_factory=dict)
    files: dict[str, "TreeNode"] = field(default_factory=dict)
    parent: Optional["TreeNode"] = None
    line_number: int = 0
    source: str = ""

    @property
    def path(self) -> str:
        """Return the relative path from the root to this node."""
        parts: list[str] = []
        node: Optional[TreeNode] = self
        while node is not None and node.parent is not None:
            parts.append(node.name)
            node = node.parent
        parts.reverse()
        return "/".join(parts)

    @property
    def relative_path(self) -> str:
        """Alias for :attr:`path`."""
        return self.path

    @property
    def is_root(self) -> bool:
        return self.parent is None

    def is_directory(self) -> bool:
        return self.kind in (NodeKind.DIRECTORY, NodeKind.AMBIGUOUS)

    def is_file(self) -> bool:
        return self.kind == NodeKind.FILE

    def resolve_to(self, kind: NodeKind) -> None:
        """Change the classification of this node."""
        self.kind = kind

    def all_files(self) -> Iterator["TreeNode"]:
        """Yield every file node beneath this node (depth-first)."""
        for f in self.files.values():
            yield f
        for child in self.children.values():
            yield from child.all_files()

    def all_directories(self) -> Iterator["TreeNode"]:
        """Yield every directory node beneath this node."""
        for child in self.children.values():
            yield child
            yield from child.all_directories()

    def total_files(self) -> int:
        return len(self.files) + sum(c.total_files() for c in self.children.values())

    def total_directories(self) -> int:
        return len(self.children) + sum(c.total_directories() for c in self.children.values())


@dataclass
class ParseError:
    """A parsing error or warning tied to a line number."""

    line_number: int
    message: str
    is_warning: bool = False


@dataclass
class ParseResult:
    """Outcome of parsing a tree string."""

    root: Optional[TreeNode] = None
    errors: list[ParseError] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(not e.is_warning for e in self.errors)

    @property
    def has_warnings(self) -> bool:
        return any(e.is_warning for e in self.errors)

    @property
    def is_valid(self) -> bool:
        return self.root is not None and not self.has_errors


# Regex for compact folder declarations:
#   "ui/ (main_window.py, spinner.py)"
# Captures the name part and the comma-separated children list.
_COMPACT_RE = re.compile(r"^(?P<name>.+?)\s*\((?P<children>[^)]*)\)\s*$")


def _classify_name(name: str) -> NodeKind:
    """Classify a name as a file, directory, or ambiguous.

    Rules:
    * Trailing ``/`` → directory.
    * Starts with ``"."`` and is longer than 1 char → file (dotfile).
    * Contains a dot (not at position 0) → file.
    * Otherwise → ambiguous.
    """
    if not name:
        return NodeKind.AMBIGUOUS
    if name.endswith("/"):
        return NodeKind.DIRECTORY
    if name.startswith(".") and len(name) > 1 and "." not in name[1:]:
        return NodeKind.FILE
    if "." in name[1:]:
        return NodeKind.FILE
    return NodeKind.AMBIGUOUS


def _is_compact_declaration(name: str) -> tuple[bool, str, list[str]]:
    """Detect a compact folder declaration.

    Returns ``(is_compact, folder_name, child_names)``.
    """
    match = _COMPACT_RE.match(name)
    if match:
        children_str = match.group("children").strip()
        children = [c.strip() for c in children_str.split(",") if c.strip()]
        folder_part = match.group("name").strip()
        return True, folder_part, children
    return False, name, []


def _extract_entry_and_depth(line: str) -> tuple[str, int]:
    """Extract the entry name and indentation depth from a single tree line.

    Handles both Unicode tree characters and space/tab indentation.
    """
    i = 0
    depth = 0
    while i < len(line):
        if line[i:i + 3] in ("├──", "└──"):
            depth += 1
            i += 3
        elif line[i] == "│":
            depth += 1
            i += 1
        elif line[i] == "─":
            i += 1  # skip horizontal line chars
        elif line[i] in (" ", "\t"):
            j = i
            while j < len(line) and line[j] in (" ", "\t"):
                j += 1
            space_count = j - i
            if j < len(line) and (line[j] in ("│", "├", "└", "─")):
                depth += space_count // 4
            i = j
        else:
            break
    name = line[i:].strip()
    return name, depth


def _count_indent_depth(line: str) -> int:
    """Return the indentation depth (in 4-space equivalents) of an indented line."""
    stripped = line.lstrip(" \t")
    leading = line[: len(line) - len(stripped)]
    return len(leading.expandtabs(4)) // 4 + 1


def _insert_dir(parent: TreeNode, name: str, line_number: int, source: str) -> TreeNode:
    """Insert or retrieve a directory node under *parent*."""
    key = name
    if key in parent.children:
        existing = parent.children[key]
        if existing.kind == NodeKind.AMBIGUOUS:
            existing.kind = NodeKind.DIRECTORY
        if not existing.source and source:
            existing.source = source
        if not existing.line_number:
            existing.line_number = line_number
        return existing
    node = TreeNode(
        name=name,
        kind=NodeKind.DIRECTORY,
        parent=parent,
        line_number=line_number,
        source=source,
    )
    parent.children[key] = node
    return node


def _insert_file(parent: TreeNode, name: str, line_number: int, source: str, kind: Optional[NodeKind] = None) -> TreeNode:
    """Insert or retrieve a file node under *parent*."""
    key = name
    if key in parent.files:
        existing = parent.files[key]
        if existing.kind == NodeKind.AMBIGUOUS and kind and kind != NodeKind.AMBIGUOUS:
            existing.kind = kind
        if not existing.source and source:
            existing.source = source
        if not existing.line_number:
            existing.line_number = line_number
        return existing
    node = TreeNode(
        name=name,
        kind=kind or _classify_name(name),
        parent=parent,
        line_number=line_number,
        source=source,
    )
    parent.files[key] = node
    return node


def _split_path(name: str) -> list[str]:
    """Split a path-like name into its components, dropping empty trailing parts.

    ``"assets/icons/"`` → ``["assets", "icons"]``
    ``"a/b/c.py"``      → ``["a", "b", "c.py"]``
    """
    parts = name.split("/")
    # Drop trailing empty string from trailing slash.
    if parts and parts[-1] == "":
        parts = parts[:-1]
    parts = [p for p in parts if p]
    return parts


def _expand_entry(
    raw_name: str,
    depth: int,
    line_number: int,
    root: TreeNode,
    stack: list[tuple[int, TreeNode]],
) -> list[tuple[int, TreeNode]]:
    """Expand a single entry into the tree, handling nested paths and compact declarations.

    Returns the updated stack.
    """
    name = raw_name.strip()
    if not name:
        return stack

    # Handle compact declaration (e.g. "ui/ (file1, file2)").
    is_compact, folder_part, child_names = _is_compact_declaration(name)
    if is_compact:
        parts = _split_path(folder_part.rstrip("/"))
        if not parts:
            parts = [folder_part] if folder_part else []

        # Navigate/create intermediate directories.
        current = _navigate_to_depth(depth, root, stack)
        for idx, part in enumerate(parts):
            is_last_dir = idx == len(parts) - 1
            if is_last_dir:
                # This is the compact folder itself.
                child = _insert_dir(current, part, line_number, name)
                stack = _push_depth(stack, depth, child)
                current = child
            else:
                child = _insert_dir(current, part, line_number, name)
                stack = _push_depth(stack, depth + idx + 1, child)
                current = child

        # Add compact children.
        for child_raw in child_names:
            child_raw = child_raw.strip()
            if not child_raw:
                continue
            child_kind = _classify_name(child_raw)
            child_parts = _split_path(child_raw.rstrip("/"))
            _add_path_parts(current, child_parts, child_raw, line_number, child_kind)

        return stack

    # Regular entry (may contain path separators).
    name_end_slash = name.endswith("/")
    parts = _split_path(name)
    if not parts:
        return stack

    current = _navigate_to_depth(depth, root, stack)

    # All parts except the last are directories.
    for idx, part in enumerate(parts[:-1]):
        child = _insert_dir(current, part, line_number, name)
        stack = _push_depth(stack, depth + idx + 1, child)
        current = child

    last = parts[-1]
    kind = _classify_name(last)
    if kind == NodeKind.DIRECTORY or name_end_slash:
        # Trailing slash on the entry name means a directory.
        clean = last.rstrip("/")
        child = _insert_dir(current, clean, line_number, name)
        stack = _push_depth(stack, depth + len(parts) - 1, child)
    elif kind == NodeKind.FILE:
        _insert_file(current, last, line_number, name, kind)
    else:
        # Ambiguous: create as directory so the user can navigate,
        # but flag it for review.
        clean = last.rstrip("/")
        child = _insert_dir(current, clean, line_number, name)
        child.kind = NodeKind.AMBIGUOUS
        stack = _push_depth(stack, depth + len(parts) - 1, child)

    return stack


def _add_path_parts(
    parent: TreeNode,
    parts: list[str],
    source: str,
    line_number: int,
    kind_hint: NodeKind,
) -> None:
    """Add a path (possibly nested) to a parent as a file or directory."""
    if not parts:
        return
    current = parent
    for idx, part in enumerate(parts[:-1]):
        current = _insert_dir(current, part, line_number, source)
    last = parts[-1]
    if kind_hint == NodeKind.DIRECTORY or last.endswith("/"):
        clean = last.rstrip("/")
        child = _insert_dir(current, clean, line_number, source)
        if kind_hint == NodeKind.AMBIGUOUS:
            child.kind = NodeKind.AMBIGUOUS
    else:
        _insert_file(current, last, line_number, source, kind_hint)


def _navigate_to_depth(
    depth: int,
    root: TreeNode,
    stack: list[tuple[int, TreeNode]],
) -> TreeNode:
    """Return the parent node at the given depth.

    If ``depth`` is 0, returns the root.  Otherwise pops the stack to find
    or fall back to a parent at ``depth - 1``.
    """
    if depth == 0:
        return root
    # Pop entries deeper than depth-1.
    target = depth - 1
    while stack and stack[-1][0] > target:
        stack.pop()
    if stack and stack[-1][0] == target:
        return stack[-1][1]
    # Fall back to root if the stack doesn't have the right depth.
    return root


def _push_depth(
    stack: list[tuple[int, TreeNode]],
    depth: int,
    node: TreeNode,
) -> list[tuple[int, TreeNode]]:
    """Update the stack, popping any entries at >= depth, then append."""
    while stack and stack[-1][0] >= depth:
        stack.pop()
    stack.append((depth, node))
    return stack


def _build_tree(
    parsed_lines: list[tuple[str, int, int]],
) -> Optional[TreeNode]:
    """Build a tree from ``(name, depth, line_number)`` tuples.

    The first line is always the root.
    """
    if not parsed_lines:
        return None

    root_name_raw, root_depth, root_line = parsed_lines[0]
    root_name = root_name_raw.rstrip("/")
    root_name = root_name.split("/")[-1]  # take last component if nested
    root = TreeNode(
        name=root_name,
        kind=NodeKind.DIRECTORY,
        parent=None,
        line_number=root_line,
        source=root_name_raw,
    )
    stack: list[tuple[int, TreeNode]] = [(0, root)]

    for name, depth, line_number in parsed_lines[1:]:
        if not name.strip():
            continue
        stack = _expand_entry(name, depth, line_number, root, stack)

    return root


def parse_tree(text: str) -> ParseResult:
    """Parse a directory-tree string into a :class:`ParseResult`.

    Auto-detects Unicode tree markers vs. plain indentation.
    """
    result = ParseResult()
    if not text or not text.strip():
        result.errors.append(ParseError(0, "Input is empty.", False))
        return result

    raw_lines = text.splitlines()
    uses_markers = any(
        "├──" in ln or "└──" in ln or "│" in ln
        for ln in raw_lines
    )

    parsed_lines: list[tuple[str, int, int]] = []
    for i, raw in enumerate(raw_lines):
        line_number = i + 1
        name = raw.strip()
        if not name:
            continue
        if uses_markers:
            entry_name, depth = _extract_entry_and_depth(raw)
        else:
            entry_name = name
            depth = _count_indent_depth(raw)
        if entry_name:
            parsed_lines.append((entry_name, depth, line_number))

    root = _build_tree(parsed_lines)

    if root is None:
        result.errors.append(ParseError(0, "Failed to parse any tree structure.", False))
        return result

    result.root = root
    _normalize_ambiguous(root)
    _mark_ambiguous(result)
    _validate_paths(root, result)
    return result


def _normalize_ambiguous(node: TreeNode) -> None:
    """Resolve ambiguous child nodes based on whether they have children.

    An ambiguous entry that contains sub-items is clearly a directory, so it
    is promoted to :attr:`NodeKind.DIRECTORY`.  An ambiguous leaf (no
    children) stays ambiguous but is moved into ``files`` so the preview can
    surface it as a candidate file that the user may promote to a directory.
    """
    to_demote: list[tuple[TreeNode, TreeNode]] = []
    for child in node.children.values():
        _normalize_ambiguous(child)
        if child.kind == NodeKind.AMBIGUOUS:
            if child.children or child.files:
                child.kind = NodeKind.DIRECTORY
            else:
                to_demote.append((node, child))
    for parent, child in to_demote:
        del parent.children[child.name]
        child.kind = NodeKind.AMBIGUOUS
        parent.files[child.name] = child


def _mark_ambiguous(result: ParseResult) -> None:
    """Flag nodes whose kind is ambiguous in the parse result."""
    if result.root is None:
        return
    for f in result.root.all_files():
        if f.kind == NodeKind.AMBIGUOUS:
            result.errors.append(
                ParseError(
                    f.line_number or 0,
                    f"Entry '{f.path}' could be a file or directory. "
                    "Clarify by adding a trailing '/' for directories or an extension for files.",
                    is_warning=True,
                )
            )
    for d in result.root.all_directories():
        if d.kind == NodeKind.AMBIGUOUS:
            result.errors.append(
                ParseError(
                    d.line_number or 0,
                    f"Entry '{d.path}' could be a file or directory. "
                    "Clarify by adding a trailing '/' for directories or an extension for files.",
                    is_warning=True,
                )
            )


def _iter_all_nodes(root: TreeNode) -> Iterator[TreeNode]:
    """Yield every node in the tree."""
    yield root
    for child in root.children.values():
        yield from _iter_all_nodes(child)
    for f in root.files.values():
        yield f


def _validate_paths(root: TreeNode, result: ParseResult) -> None:
    """Reject unsafe path components (traversal, absolute, drive letters, null bytes).

    Source-level checks are deduplicated so that a single entry like
    ``../escape`` produces one error rather than one per path component.
    """
    dangerous_re = re.compile(r"^[A-Za-z]:")
    checked_sources: set[tuple[int, str]] = set()

    def _check_source(source: str, line: int) -> None:
        key = (line, source)
        if key in checked_sources:
            return
        checked_sources.add(key)
        if not source:
            return
        if source.startswith("/") or source.startswith("\\"):
            result.errors.append(ParseError(line, f"Absolute path detected: '{source}'.", False))
        if "\x00" in source:
            result.errors.append(ParseError(line, f"Null byte in path: '{source}'.", False))
        if dangerous_re.match(source):
            result.errors.append(ParseError(line, f"Windows drive prefix detected: '{source}'.", False))

    def _check_name(name: str, line: int) -> None:
        if name.startswith("/") or name.startswith("\\"):
            result.errors.append(ParseError(line, f"Absolute path component: '{name}'.", False))
        if name == "..":
            result.errors.append(ParseError(line, f"Parent-directory traversal detected: '{name}'.", False))
        elif ".." in name:
            result.errors.append(ParseError(line, f"Parent-directory traversal in component: '{name}'.", False))
        if "\x00" in name:
            result.errors.append(ParseError(line, f"Null byte in name: '{name}'.", False))
        if dangerous_re.match(name):
            result.errors.append(ParseError(line, f"Windows drive prefix in component: '{name}'.", False))

    for node in _iter_all_nodes(root):
        _check_source(node.source, node.line_number or 0)
        _check_name(node.name, node.line_number or 0)
