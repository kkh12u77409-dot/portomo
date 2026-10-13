"""Tests for the settings service and persisted preferences."""

from __future__ import annotations

from app.settings_service import SettingsService


def test_default_language_is_english(qapp):
    settings = SettingsService("TreeForgeTest")
    settings._qsettings.clear()
    settings._cache.clear()
    assert settings.get_language() == "en"


def test_default_theme_is_dark(qapp):
    settings = SettingsService("TreeForgeTest2")
    settings._qsettings.clear()
    settings._cache.clear()
    assert settings.get_theme() == "dark"


def test_persist_and_restore_language(qapp):
    settings = SettingsService("TreeForgeTest3")
    settings.set("language", "ar")
    settings.set("theme", "light")
    # A fresh instance reading the same backend should see the values.
    settings2 = SettingsService("TreeForgeTest3")
    assert settings2.get_language() == "ar"
    assert settings2.get_theme() == "light"


def test_window_geometry_persistence(qapp):
    settings = SettingsService("TreeForgeTest4")
    settings.save_window_geometry(10, 20, 1400, 900)
    assert settings.window_geometry() == (10, 20, 1400, 900)


def test_recent_projects_add_and_clear(qapp):
    settings = SettingsService("TreeForgeTest5")
    settings.clear_recent_projects()
    settings.add_recent_project("/home/user/proj1")
    settings.add_recent_project("/home/user/proj2")
    projects = settings.get_recent_projects()
    assert "/home/user/proj1" in projects
    assert "/home/user/proj2" in projects
    settings.clear_recent_projects()
    assert settings.get_recent_projects() == []


def test_recent_projects_dedup_and_order(qapp):
    settings = SettingsService("TreeForgeTest6")
    settings.clear_recent_projects()
    settings.add_recent_project("/a")
    settings.add_recent_project("/b")
    settings.add_recent_project("/a")
    projects = settings.get_recent_projects()
    assert projects[0] == "/a"
    assert len(projects) == 2


def test_recent_projects_capped(qapp):
    settings = SettingsService("TreeForgeTest7")
    settings.clear_recent_projects()
    settings.set("max_recent_projects", 3)
    for i in range(10):
        settings.add_recent_project(f"/p{i}")
    assert len(settings.get_recent_projects()) == 3


def test_editor_settings(qapp):
    settings = SettingsService("TreeForgeTest8")
    editor = settings.get_editor_settings()
    assert "font_family" in editor
    assert "font_size" in editor
    assert isinstance(editor["font_size"], int)


def test_conflict_policy(qapp):
    settings = SettingsService("TreeForgeTest9")
    settings.set("conflict_policy", "backup")
    assert settings.get_conflict_policy() == "backup"


def test_clear_all_settings(qapp):
    settings = SettingsService("TreeForgeTest10")
    settings.set("language", "ar")
    settings.set("theme", "light")
    settings.clear_all_settings()
    assert settings.get_language() == "en"
    assert settings.get_theme() == "dark"


def test_theme_persistence_survives_reinstantiation(qapp):
    settings = SettingsService("TreeForgeTest11")
    settings.set("theme", "light")
    settings.set("language", "ar")
    reloaded = SettingsService("TreeForgeTest11")
    assert reloaded.get_theme() == "light"
    assert reloaded.get_language() == "ar"
