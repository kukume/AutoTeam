import logging

from autoteam import setup_wizard


def test_check_and_setup_returns_true_when_api_key_exists(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("API_KEY=existing-token\n", encoding="utf-8")

    monkeypatch.setattr(setup_wizard, "ENV_FILE", env_file)
    monkeypatch.setattr(setup_wizard, "ENV_EXAMPLE", tmp_path / ".env.example")
    for key in (
        "CLOUDMAIL_BASE_URL",
        "CLOUDMAIL_EMAIL",
        "CLOUDMAIL_PASSWORD",
        "CLOUDMAIL_DOMAIN",
        "CPA_URL",
        "CPA_KEY",
        "API_KEY",
    ):
        monkeypatch.delenv(key, raising=False)

    assert setup_wizard.check_and_setup() is True


def test_check_and_setup_auto_generates_api_key_when_missing(tmp_path, monkeypatch, caplog):
    env_file = tmp_path / ".env"
    env_file.write_text("", encoding="utf-8")

    monkeypatch.setattr(setup_wizard, "ENV_FILE", env_file)
    monkeypatch.setattr(setup_wizard, "ENV_EXAMPLE", tmp_path / ".env.example")
    monkeypatch.setattr("secrets.token_urlsafe", lambda _n: "auto-generated-token")
    for key in (
        "CLOUDMAIL_BASE_URL",
        "CLOUDMAIL_EMAIL",
        "CLOUDMAIL_PASSWORD",
        "CLOUDMAIL_DOMAIN",
        "CPA_URL",
        "CPA_KEY",
        "API_KEY",
    ):
        monkeypatch.delenv(key, raising=False)

    with caplog.at_level(logging.INFO):
        ok = setup_wizard.check_and_setup()

    assert ok is True
    assert "auto-generated-token" in caplog.text
    import os
    assert os.environ.get("API_KEY") == "auto-generated-token"
