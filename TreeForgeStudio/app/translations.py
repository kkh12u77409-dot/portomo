"""Centralised localization module for TreeForge Studio.

All user-facing strings are defined here so they never get scattered
throughout the UI code.  Two languages are fully supported:

* ``en`` — English (left-to-right)
* ``ar`` — Arabic  (right-to-left)
"""

from __future__ import annotations


_ENTRIES: dict[str, dict[str, str]] = {}


def _build_strings() -> None:
    """Populate the :data:`_ENTRIES` table with both languages."""

    en: dict[str, str] = {
        # Application
        "app_name": "TreeForge Studio",
        "app_version": "Version {version}",
        # Main window
        "menu_file": "File",
        "menu_edit": "Edit",
        "menu_view": "View",
        "menu_tools": "Tools",
        "menu_help": "Help",
        "menu_new": "New Project",
        "menu_open": "Open Project",
        "menu_save": "Save",
        "menu_save_as": "Save As",
        "menu_close": "Close",
        "menu_close_all": "Close All",
        "menu_exit": "Exit",
        "menu_settings": "Settings",
        "menu_about": "About",
        "action_new": "New Project",
        "action_open": "Open Project",
        "action_save": "Save",
        "action_save_all": "Save All",
        "action_close": "Close Tab",
        "action_close_all": "Close All Tabs",
        "action_exit": "Exit",
        "action_settings": "Settings",
        "action_about": "About TreeForge Studio",
        "action_about_qt": "About Qt",
        # Sidebar / navigation
        "sidebar_dashboard": "Dashboard",
        "sidebar_explorer": "Project Explorer",
        "sidebar_batch": "Batch Editor",
        "sidebar_settings": "Settings",
        # Dashboard / tree input
        "tree_input_label": "Directory Tree",
        "tree_placeholder": (
            "Paste your directory tree here...\n\n"
            "Examples:\n"
            "  Project/\n"
            "  ├── main.py\n"
            "  ├── ui/ (main_window.py, styles.py)\n"
            "  └── tests/ (test_main.py)\n\n"
            "Or use indentation:\n"
            "  Project/\n"
            "      main.py\n"
            "      ui/\n"
            "          main_window.py\n"
        ),
        "parse_button": "Parse Tree",
        "parse_button_short": "Parse",
        "create_button": "Create Structure",
        "create_confirm": "Create Structure",
        # Destination
        "destination_label": "Destination",
        "destination_placeholder": "Select or enter destination folder...",
        "browse_button": "Browse",
        "root_created": "Root: {root}",
        "destination_invalid": "Invalid or inaccessible destination.",
        "destination_empty": "Please select a destination folder.",
        # Validation / errors
        "validation_error": "Validation Error",
        "validation_warning": "Warnings",
        "parse_error": "Parsing failed. Fix the following errors:",
        "parse_warning": "Parsing completed with warnings:",
        "no_tree_defined": "No directory tree to create. Paste a tree first.",
        "errors_found": "{count} error(s) found",
        "warnings_found": "{count} warning(s) found",
        # Creation summary
        "creation_summary": "Structure Creation Summary",
        "dirs_created": "Directories created: {n}",
        "files_created": "Files created: {n}",
        "items_skipped": "Skipped (existing): {n}",
        "items_backed_up": "Backed up: {n}",
        "items_failed": "Failed: {n}",
        "creation_complete": "Structure created successfully.",
        "creation_failed": "Structure creation completed with errors.",
        # Conflict policy
        "policy_skip": "Skip existing files",
        "policy_backup": "Backup and overwrite",
        "policy_error": "Stop on conflict",
        "conflict_detected": "File Conflicts Detected",
        "conflict_detail": "The following files already exist:",
        "conflict_proceed": "Proceed",
        "conflict_cancel": "Cancel",
        # Preview / explorer
        "preview_label": "Tree Preview",
        "preview_empty": "No tree has been parsed yet.",
        "explorer_label": "Project Explorer",
        "explorer_empty": "No project loaded.",
        "search_placeholder": "Search files and folders...",
        "relative_path": "Relative Path",
        "file_type": "Type",
        "file_type_file": "File",
        "file_type_dir": "Directory",
        "file_type_ambiguous": "Ambiguous",
        "set_as_file": "Mark as File",
        "set_as_directory": "Mark as Directory",
        "refresh": "Refresh",
        # Editor
        "editor_new": "New File",
        "editor_modified_indicator": "*",
        "editor_encoding": "UTF-8",
        "editor_read_only": "Read-Only",
        "editor_unsaved_changes": "You have unsaved changes.",
        "editor_save_failed": "Failed to save: {error}",
        "editor_saved": "Saved: {path}",
        "editor_save_as_title": "Save As",
        "editor_binary_file": "Binary File Detected",
        "editor_binary_msg": "This file appears to be binary and cannot be edited as text.",
        "editor_force_edit": "Force Text Edit",
        "editor_cancel": "Cancel",
        "editor_line_col": "Line {line}, Column {col}",
        "editor_select_file": "Select a file to edit",
        "editor_no_tabs": "No open files",
        "editor_tab_close": "Close",
        # Find / Replace
        "find_replace": "Find & Replace",
        "find_placeholder": "Find",
        "replace_placeholder": "Replace",
        "find_next": "Next",
        "find_prev": "Previous",
        "find_replace_btn": "Replace",
        "find_replace_all": "Replace All",
        "find_wrap": "Wrap around",
        "find_case": "Case sensitive",
        "find_whole": "Whole words",
        "find_close": "Close",
        "find_not_found": "Not found: '{text}'",
        # Batch editing
        "batch_same_text": "Apply Same Text to Selected Files",
        "batch_content_label": "Content",
        "batch_content_placeholder": "Enter text to write to all selected files...",
        "batch_mode": "Write Mode",
        "batch_apply": "Apply to Selected Files",
        "batch_preview": "Batch Write Preview",
        "batch_preview_msg": "This will {mode} the content of {count} selected file(s).",
        "batch_preview_overwrite": "This will REPLACE the entire content of {count} file(s).",
        "batch_preview_append": "This will APPEND text to {count} file(s).",
        "batch_preview_prepend": "This will PREPEND text to {count} file(s).",
        "batch_results": "Batch Write Results",
        "batch_success": "Successfully wrote to {n} file(s).",
        "batch_skipped": "Skipped {n} file(s).",
        "batch_failed": "Failed to write {n} file(s).",
        "batch_select_files": "Please select files in the Project Explorer.",
        "batch_none_selected": "No files selected.",
        # Multi-file editor
        "multi_file_editor": "Multi-File Editor",
        "multi_save_all": "Save All",
        "multi_save_all_short": "Save All",
        "multi_saved_one": "Saved: {name}",
        "multi_saved_all": "Saved all {n} file(s).",
        "multi_save_failed_one": "Failed to save {name}: {error}",
        "multi_unsaved_warn": "You have unsaved changes in {count} file(s).",
        "multi_force_close": "Discard and Close",
        "multi_cancel_close": "Cancel",
        # Batch content format
        "batch_format_label": "Batch Content Format",
        "batch_format_placeholder": (
            "=== FILE: path/to/file.ext ===\n"
            "content here\n"
            "\n"
            "=== FILE: another.ext ===\n"
            "more content\n"
        ),
        "batch_format_parse": "Parse Batch Content",
        "batch_format_preview": "Parsed Files",
        "batch_format_count": "{count} file(s) detected",
        "batch_format_apply": "Apply to Files",
        "batch_format_empty": "No batch content parsed.",
        # Settings
        "settings_title": "Settings",
        "settings_general": "General",
        "settings_editor": "Editor",
        "settings_filesystem": "Filesystem",
        "settings_language": "Language",
        "settings_theme": "Theme",
        "settings_theme_light": "Light",
        "settings_theme_dark": "Dark",
        "settings_theme_system": "System",
        "settings_sidebar": "Show Sidebar",
        "settings_hidden_files": "Show Hidden Files",
        "settings_font_family": "Font Family",
        "settings_font_size": "Font Size",
        "settings_tab_spaces": "Tab Width (spaces)",
        "settings_show_whitespace": "Show Whitespace",
        "settings_auto_indent": "Auto Indent",
        "settings_conflict_policy": "Conflict Policy",
        "settings_create_backups": "Create Backups Before Replace",
        "settings_recent_projects": "Recent Projects",
        "settings_clear_recent": "Clear Recent Projects",
        "settings_restore_defaults": "Restore Default Settings",
        "settings_save_success": "Settings saved.",
        # Status bar
        "status_ready": "Ready",
        "status_connected": "Connected",
        "status_offline": "Offline",
        "status_chars": "{n} characters",
        "status_lines": "{n} lines",
        "status_words": "{n} words",
        "status_language": "Language: {lang}",
        "status_theme": "Theme: {theme}",
        # Dialogs
        "dialog_title_parse_errors": "Parsing Errors",
        "dialog_title_settings": "Settings",
        "dialog_title_about": "About TreeForge Studio",
        "dialog_title_batch_confirm": "Confirm Batch Write",
        "dialog_title_save_changes": "Save Changes",
        "dialog_save_msg": "Save changes to '{filename}'?",
        "dialog_save_yes": "Save",
        "dialog_save_no": "Don't Save",
        "dialog_save_cancel": "Cancel",
        # Tooltips
        "tt_new": "Create a new project tree (Ctrl+N)",
        "tt_open": "Open a project folder (Ctrl+O)",
        "tt_save": "Save current file (Ctrl+S)",
        "tt_save_all": "Save all open files (Ctrl+Shift+S)",
        "tt_undo": "Undo (Ctrl+Z)",
        "tt_redo": "Redo (Ctrl+Y)",
        "tt_cut": "Cut (Ctrl+X)",
        "tt_copy": "Copy (Ctrl+C)",
        "tt_paste": "Paste (Ctrl+V)",
        "tt_find": "Find & Replace (Ctrl+F)",
        "tt_theme": "Switch theme",
        "tt_language": "Switch language",
        "tt_refresh": "Refresh project tree",
        "tt_browse": "Browse for a destination folder",
        "tt_parse": "Parse the directory tree text",
        "tt_create": "Create the directory and file structure",
        # Shortcuts
        "shortcut_new": "Ctrl+N",
        "shortcut_open": "Ctrl+O",
        "shortcut_save": "Ctrl+S",
        "shortcut_save_all": "Ctrl+Shift+S",
        "shortcut_find": "Ctrl+F",
        "shortcut_close_tab": "Ctrl+W",
        "shortcut_close": "Ctrl+Q",
    }

    ar: dict[str, str] = {
        # Application
        "app_name": "TreeForge استوديو",
        "app_version": "الإصدار {version}",
        # Main window
        "menu_file": "ملف",
        "menu_edit": "تحرير",
        "menu_view": "عرض",
        "menu_tools": "أدوات",
        "menu_help": "مساعدة",
        "menu_new": "مشروع جديد",
        "menu_open": "فتح مشروع",
        "menu_save": "حفظ",
        "menu_save_as": "حفظ باسم",
        "menu_close": "إغلاق",
        "menu_close_all": "إغلاق الكل",
        "menu_exit": "خروج",
        "menu_settings": "الإعدادات",
        "menu_about": "عن التطبيق",
        "action_new": "مشروع جديد",
        "action_open": "فتح مشروع",
        "action_save": "حفظ",
        "action_save_all": "حفظ الكل",
        "action_close": "إغلاق تبويب",
        "action_close_all": "إغلاق جميع التبويبات",
        "action_exit": "خروج",
        "action_settings": "الإعدادات",
        "action_about": "عن TreeForge استوديو",
        "action_about_qt": "عن Qt",
        # Sidebar / navigation
        "sidebar_dashboard": "لوحة البيانات",
        "sidebar_explorer": "استكشاف المشروع",
        "sidebar_batch": "محرر دفئي",
        "sidebar_settings": "الإعدادات",
        # Dashboard / tree input
        "tree_input_label": "شجرة الدليل",
        "tree_placeholder": (
            "الصق شجرة الدليل هنا...\n\n"
            "أمثلة:\n"
            "  Project/\n"
            "  ├── main.py\n"
            "  ├── ui/ (main_window.py, styles.py)\n"
            "  └── tests/ (test_main.py)\n\n"
            "أو استخدم المسافة البادئة:\n"
            "  Project/\n"
            "      main.py\n"
            "      ui/\n"
            "          main_window.py\n"
        ),
        "parse_button": "تحليل الشجرة",
        "parse_button_short": "تحليل",
        "create_button": "إنشاء البنية",
        "create_confirm": "إنشاء البنية",
        # Destination
        "destination_label": "وجهة الحفظ",
        "destination_placeholder": "حدد أو أدخل مجلد الوجهة...",
        "browse_button": "تصفح",
        "root_created": "الجذر: {root}",
        "destination_invalid": "وجهة غير صالحة أو غير قابلة للوصول.",
        "destination_empty": "يرجى اختيار مجلد وجهة.",
        # Validation / errors
        "validation_error": "خطأ في التحقق",
        "validation_warning": "تحذيرات",
        "parse_error": "فشل التحليل. صلح الأخطاء التالية:",
        "parse_warning": "اكتمل التحليل مع تحذيرات:",
        "no_tree_defined": "لا توجد شجرة دليل لإنشائها. الصق شجرة أولاً.",
        "errors_found": "تم العثور على {count} خطأ",
        "warnings_found": "تم العثور على {count} تحذير",
        # Creation summary
        "creation_summary": "ملخص إنشاء البنية",
        "dirs_created": "تم إنشاء المجلدات: {n}",
        "files_created": "تم إنشاء الملفات: {n}",
        "items_skipped": "تم تخطيها (موجودة): {n}",
        "items_backed_up": "تم النسخ الاحتياطي: {n}",
        "items_failed": "فشل: {n}",
        "creation_complete": "تم إنشاء البنية بنجاح.",
        "creation_failed": "اكتمل إنشاء البنية مع أخطاء.",
        # Conflict policy
        "policy_skip": "تخطي الملفات الموجودة",
        "policy_backup": "النسخ الاحتياطي ثم الاستبدال",
        "policy_error": "إيقاف عند التعارض",
        "conflict_detected": "تم اكتشاف تعارض في الملفات",
        "conflict_detail": "الملفات التالية موجودة بالفعل:",
        "conflict_proceed": "متابعة",
        "conflict_cancel": "إلغاء",
        # Preview / explorer
        "preview_label": "معاينة الشجرة",
        "preview_empty": "لم يتم تحليل أي شجرة بعد.",
        "explorer_label": "استكشاف المشروع",
        "explorer_empty": "لا يوجد مشروع محمل.",
        "search_placeholder": "ابحث عن الملفات والمجلدات...",
        "relative_path": "المسار النسبي",
        "file_type": "النوع",
        "file_type_file": "ملف",
        "file_type_dir": "مجلد",
        "file_type_ambiguous": "غامض",
        "set_as_file": "تصنيف كملف",
        "set_as_directory": "تصنيف كمجلد",
        "refresh": "تحديث",
        # Editor
        "editor_new": "ملف جديد",
        "editor_modified_indicator": "*",
        "editor_encoding": "UTF-8",
        "editor_read_only": "للقراءة فقط",
        "editor_unsaved_changes": "لديك تغييرات غير محفوظة.",
        "editor_save_failed": "فشل الحفظ: {error}",
        "editor_saved": "تم الحفظ: {path}",
        "editor_save_as_title": "حفظ باسم",
        "editor_binary_file": "تم اكتشاف ملف ثنائي",
        "editor_binary_msg": "يبدو أن هذا الملف ثنائي ولا يمكن تحريره كنص.",
        "editor_force_edit": "تحرير نصي إجباري",
        "editor_cancel": "إلغاء",
        "editor_line_col": "السطر {line}، العمود {col}",
        "editor_select_file": "حدد ملف للتحرير",
        "editor_no_tabs": "لا توجد ملفات مفتوحة",
        "editor_tab_close": "إغلاق",
        # Find / Replace
        "find_replace": "البحث والاستبدال",
        "find_placeholder": "بحث",
        "replace_placeholder": "استبدال",
        "find_next": "التالي",
        "find_prev": "السابق",
        "find_replace_btn": "استبدال",
        "find_replace_all": "استبدال الكل",
        "find_wrap": "الالتفاف",
        "find_case": "حساسية الأحرف",
        "find_whole": "كلمات كاملة",
        "find_close": "إغلاق",
        "find_not_found": "غير موجود: '{text}'",
        # Batch editing
        "batch_same_text": "تطبيق نفس النص على الملفات المحددة",
        "batch_content_label": "المحتوى",
        "batch_content_placeholder": "أدخل النص للكتابة في جميع الملفات المحددة...",
        "batch_mode": "وضعية الكتابة",
        "batch_apply": "تطبيق على الملفات المحددة",
        "batch_preview": "معاينة كتابة الدفئية",
        "batch_preview_msg": "سيتم {mode} محتوى {count} ملف(ات) محدد(ة).",
        "batch_preview_overwrite": "سيتم استبدال محتوى {count} ملف(ات) بالكامل.",
        "batch_preview_append": "سيتم إضافة نص إلى {count} ملف(ات).",
        "batch_preview_prepend": "سيتم إضافة نص في بداية {count} ملف(ات).",
        "batch_results": "نتائج كتابة الدفئية",
        "batch_success": "تم الكتابة بنجاح في {n} ملف(ات).",
        "batch_skipped": "تم تخطي {n} ملف(ات).",
        "batch_failed": "فشل في الكتابة في {n} ملف(ات).",
        "batch_select_files": "يرجى تحديد ملفات في استكشاف المشروع.",
        "batch_none_selected": "لم يتم تحديد أي ملفات.",
        # Multi-file editor
        "multi_file_editor": "محرر متعدد الملفات",
        "multi_save_all": "حفظ الكل",
        "multi_save_all_short": "حفظ الكل",
        "multi_saved_one": "تم الحفظ: {name}",
        "multi_saved_all": "تم حفظ جميع {n} ملف(ات).",
        "multi_save_failed_one": "فشل في حفظ {name}: {error}",
        "multi_unsaved_warn": "لديك تغييرات غير محفوظة في {count} ملف(ات).",
        "multi_force_close": "تجاهل وإغلاق",
        "multi_cancel_close": "إلغاء",
        # Batch content format
        "batch_format_label": "تنسيق المحتوى الدفئي",
        "batch_format_placeholder": (
            "=== FILE: path/to/file.ext ===\n"
            "المحتوى هنا\n"
            "\n"
            "=== FILE: another.ext ===\n"
            "محتوى إضافي\n"
        ),
        "batch_format_parse": "تحليل المحتوى الدفئي",
        "batch_format_preview": "الملفات المكتشفة",
        "batch_format_count": "تم اكتشاف {count} ملف(ات)",
        "batch_format_apply": "تطبيق على الملفات",
        "batch_format_empty": "لم يتم تحليل أي محتوى دفئي.",
        # Settings
        "settings_title": "الإعدادات",
        "settings_general": "عام",
        "settings_editor": "المحرر",
        "settings_filesystem": "نظام الملفات",
        "settings_language": "اللغة",
        "settings_theme": "السمة",
        "settings_theme_light": "فاتح",
        "settings_theme_dark": "مظلم",
        "settings_theme_system": "النظام",
        "settings_sidebar": "إظهار الشريط الجانبي",
        "settings_hidden_files": "إظهار الملفات المخفية",
        "settings_font_family": "عائلة الخط",
        "settings_font_size": "حجم الخط",
        "settings_tab_spaces": "عرض الجدلة (مسافات)",
        "settings_show_whitespace": "إظهار الفراغات",
        "settings_auto_indent": "المسافة التركيبية التلقائية",
        "settings_conflict_policy": "سياسة التعارض",
        "settings_create_backups": "إنشاء نسخ احتياطية قبل الاستبدال",
        "settings_recent_projects": "المشاريع الأخيرة",
        "settings_clear_recent": "مسح المشاريع الأخيرة",
        "settings_restore_defaults": "استعادة الإعدادات الافتراضية",
        "settings_save_success": "تم حفظ الإعدادات.",
        # Status bar
        "status_ready": "جاهز",
        "status_connected": "متصل",
        "status_offline": "غير متصل",
        "status_chars": "{n} حرف",
        "status_lines": "{n} سطر",
        "status_words": "{n} كلمة",
        "status_language": "اللغة: {lang}",
        "status_theme": "السمة: {theme}",
        # Dialogs
        "dialog_title_parse_errors": "أخطاء التحليل",
        "dialog_title_settings": "الإعدادات",
        "dialog_title_about": "عن TreeForge استوديو",
        "dialog_title_batch_confirm": "تأكيد كتابة الدفئية",
        "dialog_title_save_changes": "حفظ التغييرات",
        "dialog_save_msg": "حفظ التغييرات في '{filename}'؟",
        "dialog_save_yes": "حفظ",
        "dialog_save_no": "عدم الحفظ",
        "dialog_save_cancel": "إلغاء",
        # Tooltips
        "tt_new": "إنشاء شجرة مشروع جديدة (Ctrl+N)",
        "tt_open": "فتح مجلد مشروع (Ctrl+O)",
        "tt_save": "حفظ الملف الحالي (Ctrl+S)",
        "tt_save_all": "حفظ جميع الملفات المفتوحة (Ctrl+Shift+S)",
        "tt_undo": "تراجع (Ctrl+Z)",
        "tt_redo": "إعادة (Ctrl+Y)",
        "tt_cut": "قص (Ctrl+X)",
        "tt_copy": "نسخ (Ctrl+C)",
        "tt_paste": "لصق (Ctrl+V)",
        "tt_find": "بحث واستبدال (Ctrl+F)",
        "tt_theme": "تبديل السمة",
        "tt_language": "تبديل اللغة",
        "tt_refresh": "تحديث شجرة المشروع",
        "tt_browse": "تصفح مجلد الوجهة",
        "tt_parse": "تحليل شجرة الدليل",
        "tt_create": "إنشاء هيكل المجلدات والملفات",
        # Shortcuts
        "shortcut_new": "Ctrl+N",
        "shortcut_open": "Ctrl+O",
        "shortcut_save": "Ctrl+S",
        "shortcut_save_all": "Ctrl+Shift+S",
        "shortcut_find": "Ctrl+F",
        "shortcut_close_tab": "Ctrl+W",
        "shortcut_close": "Ctrl+Q",
    }

    # English fallbacks for any missing Arabic entries.
    for key, value in en.items():
        ar.setdefault(key, value)

    _ENTRIES["en"] = en
    _ENTRIES["ar"] = ar


def tr(key: str, **kwargs: object) -> str:
    """Translate *key* using the currently-selected language.

    If no language has been set, English is used.
    """
    if not _ENTRIES:
        _build_strings()
    lang = _current_language()
    table = _ENTRIES.get(lang, _ENTRIES["en"])
    text = table.get(key, _ENTRIES["en"].get(key, key))
    try:
        return text.format(**kwargs)
    except (KeyError, ValueError, IndexError):
        return text


_current_lang: str = "en"


def set_language(lang: str) -> None:
    """Set the active language (must be 'en' or 'ar')."""
    global _current_lang
    if lang not in _ENTRIES:
        _build_strings()
    if lang in _ENTRIES:
        _current_lang = lang
    else:
        _current_lang = "en"


def _current_language() -> str:
    if not _ENTRIES:
        _build_strings()
    return _current_lang


def is_rtl() -> bool:
    """Return True if the current language is right-to-left."""
    return _current_language() == "ar"


def get_translation_table() -> dict[str, str]:
    """Return the full translation table for the current language."""
    if not _ENTRIES:
        _build_strings()
    return _ENTRIES.get(_current_language(), _ENTRIES["en"])


def available_languages() -> list[tuple[str, str]]:
    """Return a list of (code, display_name) pairs."""
    if not _ENTRIES:
        _build_strings()
    return [
        ("en", "English"),
        ("ar", "العربية"),
    ]


# Build the tables on import.
_build_strings()
