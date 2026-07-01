from autoteam import sync_targets


def test_get_sync_target_states_uses_implicit_config_presence():
    env = {
        "CPA_URL": "http://127.0.0.1:8317",
        "CPA_KEY": "key-1",
    }

    assert sync_targets.get_sync_target_states(env) == {
        "cpa": True,
    }


def test_get_sync_target_states_respects_explicit_toggle_override():
    env = {
        "SYNC_TARGET_CPA": "false",
        "CPA_URL": "http://127.0.0.1:8317",
        "CPA_KEY": "key-1",
    }

    assert sync_targets.get_sync_target_states(env) == {
        "cpa": False,
    }


def test_describe_sync_targets_formats_labels():
    assert sync_targets.describe_sync_targets(["cpa"]) == "CPA"


def test_get_available_sync_targets_keeps_explicitly_disabled_targets_for_cleanup():
    env = {
        "SYNC_TARGET_CPA": "false",
        "CPA_URL": "http://127.0.0.1:8317",
        "CPA_KEY": "key-1",
    }

    assert sync_targets.get_available_sync_targets(env) == ["cpa"]


def test_delete_account_from_configured_targets_include_disabled_uses_disabled_target_cleanup(monkeypatch):
    monkeypatch.setenv("SYNC_TARGET_CPA", "false")
    monkeypatch.setenv("CPA_URL", "http://127.0.0.1:8317")
    monkeypatch.setenv("CPA_KEY", "key-1")

    calls = []

    def fake_delete_from_cpa(name):
        calls.append(name)
        return True

    monkeypatch.setattr(
        "autoteam.cpa_sync.list_cpa_files",
        lambda: [{"email": "user@example.com", "name": "codex-user@example.com-team.json"}],
    )
    monkeypatch.setattr("autoteam.cpa_sync.delete_from_cpa", fake_delete_from_cpa)

    result = sync_targets.delete_account_from_configured_targets(
        "user@example.com",
        auth_names=["codex-user@example.com-team.json"],
        include_disabled=True,
    )

    assert calls == ["codex-user@example.com-team.json"]
    assert result == {
        "cpa": {"deleted": ["codex-user@example.com-team.json"], "count": 1},
    }
