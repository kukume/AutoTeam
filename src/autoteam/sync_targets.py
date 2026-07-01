"""统一远端同步目标分发：CPA。"""

from __future__ import annotations

import logging
import os
from collections.abc import Mapping

logger = logging.getLogger(__name__)

SYNC_TARGET_CPA = "cpa"

_SYNC_TARGET_META = {
    SYNC_TARGET_CPA: {
        "label": "CPA",
        "config_keys": ("CPA_URL", "CPA_KEY"),
    },
}


def _normalize_env(env: Mapping[str, object] | None = None) -> dict[str, str]:
    source = env or os.environ
    return {str(key): "" if value is None else str(value) for key, value in source.items()}


def get_sync_target_meta(target: str) -> dict[str, object]:
    try:
        return _SYNC_TARGET_META[target]
    except KeyError as exc:
        raise KeyError(f"未知同步目标: {target}") from exc


def get_sync_target_states(env: Mapping[str, object] | None = None) -> dict[str, bool]:
    values = _normalize_env(env)
    return {
        target: all((values.get(key) or "").strip() for key in tuple(meta["config_keys"]))
        for target, meta in _SYNC_TARGET_META.items()
    }


def is_sync_target_enabled(target: str, env: Mapping[str, object] | None = None) -> bool:
    return get_sync_target_states(env).get(target, False)


def get_enabled_sync_targets(env: Mapping[str, object] | None = None) -> list[str]:
    states = get_sync_target_states(env)
    return [target for target in _SYNC_TARGET_META if states.get(target)]


def get_sync_target_labels(targets: list[str] | None = None) -> list[str]:
    if targets is None:
        targets = list(_SYNC_TARGET_META)
    return [str(_SYNC_TARGET_META[target]["label"]) for target in targets if target in _SYNC_TARGET_META]


def describe_sync_targets(targets: list[str] | None = None) -> str:
    labels = get_sync_target_labels(targets)
    if not labels:
        return "未启用远端同步目标"
    return " + ".join(labels)


def get_missing_target_configs(
    targets: list[str] | None = None, env: Mapping[str, object] | None = None
) -> list[tuple[str, str]]:
    values = _normalize_env(env)
    missing: list[tuple[str, str]] = []
    for target in targets or []:
        meta = get_sync_target_meta(target)
        for key in tuple(meta["config_keys"]):
            value = (values.get(key) or "").strip()
            if not value:
                missing.append((key, str(meta["label"])))
    return missing


def sync_to_configured_targets():
    results = {}
    enabled_targets = get_enabled_sync_targets()

    if SYNC_TARGET_CPA in enabled_targets:
        from autoteam.cpa_sync import sync_to_cpa

        results[SYNC_TARGET_CPA] = sync_to_cpa()

    return results


def sync_main_codex_to_configured_targets(filepath: str):
    results = {}
    enabled_targets = get_enabled_sync_targets()

    if SYNC_TARGET_CPA in enabled_targets:
        from autoteam.cpa_sync import sync_main_codex_to_cpa

        results[SYNC_TARGET_CPA] = sync_main_codex_to_cpa(filepath)

    return results


def delete_main_codex_from_configured_targets():
    results = {}
    targets = get_enabled_sync_targets()

    if SYNC_TARGET_CPA in targets:
        from autoteam.cpa_sync import delete_main_codex_from_cpa

        try:
            results[SYNC_TARGET_CPA] = delete_main_codex_from_cpa()
        except Exception as exc:
            logger.warning("[CPA] 删除主号失败: %s", exc)
            results[SYNC_TARGET_CPA] = {"deleted": [], "count": 0, "error": str(exc)}

    return results


def delete_account_from_configured_targets(
    email: str, *, auth_names: list[str] | None = None
):
    results = {}
    targets = get_enabled_sync_targets()

    if SYNC_TARGET_CPA in targets:
        from autoteam.cpa_sync import delete_from_cpa, list_cpa_files

        try:
            deleted = []
            auth_name_set = set(auth_names or [])
            for item in list_cpa_files():
                item_email = (item.get("email") or "").lower()
                item_name = item.get("name") or ""
                if item_email == email.lower() or item_name in auth_name_set:
                    if delete_from_cpa(item_name):
                        deleted.append(item_name)
            results[SYNC_TARGET_CPA] = {"deleted": deleted, "count": len(deleted)}
        except Exception as exc:
            logger.warning("[CPA] 删除账号 %s 失败: %s", email, exc)
            results[SYNC_TARGET_CPA] = {"deleted": [], "count": 0, "error": str(exc)}

    return results
