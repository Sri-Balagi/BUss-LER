import os
from unittest.mock import mock_open, patch

import pytest

from app.sdk.manifest.app_manifest import AppManifest
from app.shell.scaffold import Scaffolder, TemplateValidator


@patch("os.path.exists")
def test_validate_app_template_no_manifest(mock_exists):
    mock_exists.return_value = False
    assert TemplateValidator.validate_app_template("test_path") is False

@patch("os.path.exists")
@patch("builtins.open", new_callable=mock_open, read_data='{"name": "test_app", "version": "1.0", "description": "test", "main": "main.py", "permissions": []}')
@patch("app.sdk.manifest.app_manifest.AppManifest.model_validate")
def test_validate_app_template_valid(mock_validate, mock_file, mock_exists):
    mock_exists.return_value = True
    assert TemplateValidator.validate_app_template("test_path") is True

@patch("os.path.exists")
@patch("builtins.open", new_callable=mock_open, read_data='invalid_json')
def test_validate_app_template_invalid(mock_file, mock_exists):
    mock_exists.return_value = True
    assert TemplateValidator.validate_app_template("test_path") is False

@patch("os.path.exists")
@patch("shutil.copytree")
@patch("app.shell.scaffold.TemplateValidator.validate_app_template")
def test_scaffolder_create_app(mock_validate, mock_copytree, mock_exists):
    mock_exists.return_value = True
    mock_validate.return_value = True

    scaffolder = Scaffolder("templates")
    assert scaffolder.create_app("test_app", "output") is True
    mock_copytree.assert_called_once()

@patch("os.path.exists")
def test_scaffolder_create_app_not_found(mock_exists):
    mock_exists.return_value = False

    scaffolder = Scaffolder("templates")
    with pytest.raises(FileNotFoundError):
        scaffolder.create_app("test_app", "output")

@patch("os.path.exists")
@patch("shutil.copytree")
@patch("shutil.rmtree")
@patch("app.shell.scaffold.TemplateValidator.validate_app_template")
def test_scaffolder_create_app_invalid(mock_validate, mock_rmtree, mock_copytree, mock_exists):
    mock_exists.return_value = True
    mock_validate.return_value = False

    scaffolder = Scaffolder("templates")
    with pytest.raises(ValueError):
        scaffolder.create_app("test_app", "output")
    mock_rmtree.assert_called_once()

@patch("os.path.exists")
@patch("shutil.copytree")
def test_scaffolder_create_plugin(mock_copytree, mock_exists):
    mock_exists.return_value = True

    scaffolder = Scaffolder("templates")
    assert scaffolder.create_plugin("test_plugin", "output") is True
    mock_copytree.assert_called_once()

@patch("os.path.exists")
def test_scaffolder_create_plugin_not_found(mock_exists):
    mock_exists.return_value = False

    scaffolder = Scaffolder("templates")
    with pytest.raises(FileNotFoundError):
        scaffolder.create_plugin("test_plugin", "output")
