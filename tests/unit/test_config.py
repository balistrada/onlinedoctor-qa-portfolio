import pytest

from qa_portfolio.config import resolve_base_url


def test_default_base_url_is_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BASE_URL", raising=False)
    monkeypatch.delenv("TEST_ENV", raising=False)
    assert resolve_base_url() == "https://veryops.kintree.eu"


def test_base_url_override_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BASE_URL", "https://staging.example.test/root/")
    assert resolve_base_url() == "https://staging.example.test/root"


def test_unknown_environment_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BASE_URL", raising=False)
    monkeypatch.setenv("TEST_ENV", "qa-does-not-exist")
    with pytest.raises(KeyError):
        resolve_base_url()


def test_credentials_in_base_url_are_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BASE_URL", "https://user:secret@veryops.kintree.eu")
    with pytest.raises(ValueError):
        resolve_base_url()


def test_test_env_local_placeholder(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BASE_URL", raising=False)
    monkeypatch.setenv("TEST_ENV", "local")
    assert resolve_base_url() == "http://127.0.0.1:4321"
