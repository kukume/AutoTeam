from autoteam import sync_targets


def test_get_sync_target_states_uses_config_presence():
    env = {
        "CPA_URL": "http://127.0.0.1:8317",
        "CPA_KEY": "key-1",
    }

    assert sync_targets.get_sync_target_states(env) == {
        "cpa": True,
    }


def test_get_sync_target_states_false_when_config_missing():
    env = {
        "CPA_URL": "http://127.0.0.1:8317",
        "CPA_KEY": "",
    }

    assert sync_targets.get_sync_target_states(env) == {
        "cpa": False,
    }


def test_describe_sync_targets_formats_labels():
    assert sync_targets.describe_sync_targets(["cpa"]) == "CPA"


def test_delete_account_from_configured_targets(monkeypatch):
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
    )

    assert calls == ["codex-user@example.com-team.json"]
    assert result == {
        "cpa": {"deleted": ["codex-user@example.com-team.json"], "count": 1},
    }
