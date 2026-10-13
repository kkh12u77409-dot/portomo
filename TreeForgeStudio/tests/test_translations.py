"""Tests for the localization module (Arabic / English)."""

from __future__ import annotations

import pytest

from app.translations import (
    tr,
    set_language,
    is_rtl,
    available_languages,
    get_translation_table,
)


@pytest.fixture(autouse=True)
def _reset_language():
    """Reset to English after each test."""
    set_language("en")
    yield
    set_language("en")


def test_english_is_default():
    assert tr("app_name") == "TreeForge Studio"


def test_arabic_switches_language():
    set_language("ar")
    assert is_rtl() is True
    assert tr("app_name") == "TreeForge استوديو"


def test_english_is_ltr():
    assert is_rtl() is False


def test_arabic_translations_exist_for_core_strings():
    set_language("ar")
    keys = [
        "parse_button",
        "create_button",
        "browse_button",
        "batch_apply",
        "settings_title",
        "explorer_label",
        "find_replace",
    ]
    for key in keys:
        text = tr(key)
        assert text, f"Missing translation for {key}"
        # Arabic translations must not fall back to the English key.
        assert text != key


def test_no_english_left_in_arabic_dialogs():
    set_language("ar")
    # Spot-check natural Arabic strings.
    assert tr("batch_apply") == "تطبيق على الملفات المحددة"
    assert tr("destination_label") == "وجهة الحفظ"


def test_format_substitution_english():
    assert tr("app_version").format(version="1.0.0").endswith("1.0.0")


def test_format_substitution_arabic():
    set_language("ar")
    result = tr("dirs_created").format(n=5)
    assert "5" in result


def test_available_languages():
    langs = available_languages()
    codes = [code for code, _ in langs]
    assert "en" in codes
    assert "ar" in codes


def test_translation_table_complete():
    en_table = get_translation_table()
    assert len(en_table) > 50
    set_language("ar")
    ar_table = get_translation_table()
    # Every English key must exist in Arabic too.
    for key in en_table:
        assert key in ar_table


def test_unknown_key_falls_back_to_key():
    assert tr("this_key_does_not_exist_xyz") == "this_key_does_not_exist_xyz"


def test_runtime_language_switch():
    assert tr("parse_button") == "Parse Tree"
    set_language("ar")
    assert tr("parse_button") == "تحليل الشجرة"
    set_language("en")
    assert tr("parse_button") == "Parse Tree"


def test_relative_path_and_extensions_mix():
    # Arabic UI must still render LTR paths correctly (no control chars added).
    set_language("ar")
    text = tr("root_created").format(root="D:\\Projects\\SumMaster")
    assert "SumMaster" in text
    assert "Projects" in text
