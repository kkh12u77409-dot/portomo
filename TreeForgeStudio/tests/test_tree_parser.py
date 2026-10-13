"""Tests for the tree parser."""

from __future__ import annotations

from app.tree_parser import NodeKind, parse_tree


SUMMASTER_TREE = """SumMaster/
├── main.py
├── make_zip.py
├── requirements.txt
├── README.md
├── assets/icons/
├── ui/ (main_window.py, spinner.py, styles.py)
├── core/ (calculator.py, worker.py)
├── services/ (settings_service.py)
└── tests/ (test_calculator.py, test_worker.py)"""


def test_parse_summaster_example() -> None:
    result = parse_tree(SUMMASTER_TREE)
    assert result.root is not None
    assert result.root.name == "SumMaster"
    assert not result.has_errors, [e.message for e in result.errors]


def test_summaster_counts() -> None:
    result = parse_tree(SUMMASTER_TREE)
    root = result.root
    assert root.total_directories() == 6  # assets, icons, ui, core, services, tests
    assert root.total_files() == 12


def test_summaster_root_files() -> None:
    result = parse_tree(SUMMASTER_TREE)
    root = result.root
    assert set(root.files.keys()) == {"main.py", "make_zip.py", "requirements.txt", "README.md"}


def test_compact_folder_expansion() -> None:
    result = parse_tree(SUMMASTER_TREE)
    ui = result.root.children["ui"]
    assert set(ui.files.keys()) == {"main_window.py", "spinner.py", "styles.py"}


def test_compact_folder_core() -> None:
    result = parse_tree(SUMMASTER_TREE)
    core = result.root.children["core"]
    assert set(core.files.keys()) == {"calculator.py", "worker.py"}


def test_nested_directories_via_slash() -> None:
    result = parse_tree(SUMMASTER_TREE)
    assets = result.root.children["assets"]
    assert "icons" in assets.children
    assert assets.children["icons"].kind == NodeKind.DIRECTORY


def test_reject_parent_traversal() -> None:
    tree = "Root/\n├── ../escape\n└── file.py"
    result = parse_tree(tree)
    assert result.has_errors
    assert any("traversal" in e.message.lower() for e in result.errors)


def test_reject_absolute_path() -> None:
    tree = "Root/\n├── /etc/passwd\n└── file.py"
    result = parse_tree(tree)
    assert result.has_errors
    assert any("absolute" in e.message.lower() for e in result.errors)


def test_reject_windows_drive() -> None:
    tree = "Root/\n├── C:/Windows\n└── file.py"
    result = parse_tree(tree)
    assert result.has_errors
    assert any("drive" in e.message.lower() for e in result.errors)


def test_reject_null_byte() -> None:
    tree = "Root/\n├── good.py\n└── ba\x00d.py"
    result = parse_tree(tree)
    assert result.has_errors


def test_dotfiles_recognised() -> None:
    tree = "Project/\n├── .gitignore\n├── .env\n└── src/"
    result = parse_tree(tree)
    root = result.root
    assert ".gitignore" in root.files
    assert ".env" in root.files
    assert root.files[".gitignore"].kind == NodeKind.FILE


def test_extensionless_file_classified_ambiguous() -> None:
    tree = "Project/\n├── Makefile\n└── main.py"
    result = parse_tree(tree)
    makefile = result.root.files["Makefile"]
    assert makefile.kind == NodeKind.AMBIGUOUS
    assert result.has_warnings


def test_trailing_slash_is_directory() -> None:
    tree = "Project/\n├── src/\n└── main.py"
    result = parse_tree(tree)
    assert "src" in result.root.children
    assert result.root.children["src"].kind == NodeKind.DIRECTORY


def test_empty_input() -> None:
    result = parse_tree("")
    assert result.has_errors


def test_indented_format() -> None:
    tree = """Project/
    main.py
    utils/
        helper.py
    ui/
        main_window.py"""
    result = parse_tree(tree)
    assert result.root.name == "Project"
    assert "utils" in result.root.children
    assert "ui" in result.root.children
    assert "helper.py" in result.root.children["utils"].files


def test_deep_tree_markers() -> None:
    tree = """Root/
├── src/
│   ├── utils/
│   │   ├── helper.py
│   │   └── config.py
│   └── main.py
└── tests/
    └── test_main.py"""
    result = parse_tree(tree)
    root = result.root
    assert "src" in root.children
    assert "utils" in root.children["src"].children
    assert "helper.py" in root.children["src"].children["utils"].files
    assert "main.py" in root.children["src"].files
    assert "test_main.py" in root.children["tests"].files


def test_node_path_property() -> None:
    tree = """Root/
├── src/
│   └── main.py
└── README.md"""
    result = parse_tree(tree)
    src_main = result.root.children["src"].files["main.py"]
    assert src_main.path == "src/main.py"


def test_compact_with_nested_folder_path() -> None:
    tree = "Root/\n└── assets/ui/ (main.py, styles.py)"
    result = parse_tree(tree)
    root = result.root
    assert root.name == "Root"
    assert "assets" in root.children
    assert "ui" in root.children["assets"].children
    ui = root.children["assets"].children["ui"]
    assert "main.py" in ui.files
    assert "styles.py" in ui.files


def test_empty_dir_from_trailing_slash() -> None:
    tree = "Project/\n├── empty_dir/\n└── main.py"
    result = parse_tree(tree)
    empty = result.root.children["empty_dir"]
    assert empty.kind == NodeKind.DIRECTORY
    assert len(empty.files) == 0
    assert len(empty.children) == 0
