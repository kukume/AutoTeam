import os

import pytest

_RUNTIME_ENV_KEYS = (
    "MAIL_PROVIDER",
    "MAIL_SERVICES_JSON",
    "MAIL_SERVICE_DEFAULT",
    "CLOUDMAIL_BASE_URL",
    "CLOUDMAIL_EMAIL",
    "CLOUDMAIL_PASSWORD",
    "CLOUDMAIL_DOMAIN",
    "CF_TEMP_EMAIL_BASE_URL",
    "CF_TEMP_EMAIL_ADMIN_PASSWORD",
    "CF_TEMP_EMAIL_DOMAIN",
    "CPA_URL",
    "CPA_KEY",
    "PLAYWRIGHT_PROXY_URL",
    "PLAYWRIGHT_PROXY_SERVER",
    "PLAYWRIGHT_PROXY_USERNAME",
    "PLAYWRIGHT_PROXY_PASSWORD",
    "PLAYWRIGHT_PROXY_BYPASS",
    "EMAIL_POLL_INTERVAL",
    "EMAIL_POLL_TIMEOUT",
    "AUTO_CHECK_INTERVAL",
    "AUTO_CHECK_TARGET_SEATS",
    "AUTO_CHECK_THRESHOLD",
    "AUTO_CHECK_MIN_LOW",
    "API_KEY",
)


@pytest.fixture(autouse=True)
def _isolate_runtime_env():
    previous = {key: os.environ.get(key) for key in _RUNTIME_ENV_KEYS}
    for key in _RUNTIME_ENV_KEYS:
        os.environ.pop(key, None)
    try:
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
