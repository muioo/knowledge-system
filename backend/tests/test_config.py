import pytest
from settings.config import settings


def test_settings_load():
    assert settings.app_name == "知识系统后端"
    assert settings.app_version == "1.0.0"


def test_database_url():
    db_url = settings.database_url
    assert "mysql://" in db_url
    assert "knowledge-system" in db_url


def test_cors_origins_list():
    origins = settings.cors_origins_list
    assert isinstance(origins, list)
    assert "http://localhost:3000" in origins
