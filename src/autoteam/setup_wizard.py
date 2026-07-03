"""首次启动初始化向导 — 交互式填写 .env 中的必填配置"""

import logging
import os
import re
import secrets
import sys

from autoteam.config import PROJECT_ROOT
from autoteam.mail_provider import (
    MAIL_PROVIDER_CLOUDFLARE_TEMP_EMAIL,
    get_default_mail_service,
    get_mail_provider_name,
    get_mail_service_display_name,
    get_mail_service_missing_fields,
    get_mail_services,
)
from autoteam.textio import parse_env_line, read_text, write_text

logger = logging.getLogger(__name__)

ENV_FILE = PROJECT_ROOT / ".env"
ENV_EXAMPLE = PROJECT_ROOT / ".env.example"

# 启动时硬性要求的配置项（目前仅 API_KEY）
STARTUP_REQUIRED_CONFIGS = [
    ("API_KEY", "API 鉴权密钥（回车自动生成）", "", False),
]

# 可在配置面板中编辑的配置项（key, 提示, 默认值, 是否可选）
REQUIRED_CONFIGS = [
    ("MAIL_PROVIDER", "邮箱服务提供者（cloudmail/cloudflare_temp_email）", "cloudmail", True),
    ("MAIL_SERVICES_JSON", "邮箱服务列表 JSON（内部使用）", "", True),
    ("MAIL_SERVICE_DEFAULT", "默认新建邮箱服务 ID（内部使用）", "", True),
    ("CLOUDMAIL_BASE_URL", "CloudMail API 地址", "", True),
    ("CLOUDMAIL_EMAIL", "CloudMail 登录邮箱", "", True),
    ("CLOUDMAIL_PASSWORD", "CloudMail 登录密码", "", True),
    ("CLOUDMAIL_DOMAIN", "CloudMail 邮箱域名（如 @example.com）", "", True),
    ("CF_TEMP_EMAIL_BASE_URL", "Cloudflare Temp Email 地址", "", True),
    ("CF_TEMP_EMAIL_ADMIN_PASSWORD", "Cloudflare Temp Email 管理密码", "", True),
    ("CF_TEMP_EMAIL_DOMAIN", "Cloudflare Temp Email 邮箱域名（如 example.com）", "", True),
    ("CPA_URL", "CPA (CLIProxyAPI) 地址", "http://127.0.0.1:8317", True),
    ("CPA_KEY", "CPA 管理密钥", "", True),
    ("PLAYWRIGHT_PROXY_URL", "Playwright 浏览器代理 URL（可选，如 socks5://host:port）", "", True),
    ("PLAYWRIGHT_PROXY_BYPASS", "Playwright 代理绕过列表（可选，如 localhost,127.0.0.1）", "", True),
    ("PHONE_OTP_AUTO_SEND", "自动发送手机验证码（off/whatsapp/sms）", "off", True),
    ("API_KEY", "API 鉴权密钥（回车自动生成）", "", False),
]


def _read_env() -> dict[str, str]:
    """读取 .env 文件为 dict"""
    result = {}
    if ENV_FILE.exists():
        for line in read_text(ENV_FILE).splitlines():
            parsed = parse_env_line(line)
            if parsed:
                key, value = parsed
                result[key] = value
    return result


def _write_env(key: str, value: str):
    """写入或更新 .env 中的某个 key"""
    if ENV_FILE.exists():
        content = read_text(ENV_FILE)
        pattern = rf"^{re.escape(key)}=.*$"
        if re.search(pattern, content, re.MULTILINE):
            content = re.sub(pattern, f"{key}={value}", content, flags=re.MULTILINE)
        else:
            content = content.rstrip() + f"\n{key}={value}\n"
        write_text(ENV_FILE, content)
    else:
        # 从 .env.example 复制再写入
        if ENV_EXAMPLE.exists():
            content = read_text(ENV_EXAMPLE)
            pattern = rf"^{re.escape(key)}=.*$"
            if re.search(pattern, content, re.MULTILINE):
                content = re.sub(pattern, f"{key}={value}", content, flags=re.MULTILINE)
            write_text(ENV_FILE, content)
        else:
            write_text(ENV_FILE, f"{key}={value}\n")


def check_and_setup(interactive: bool = True) -> bool:
    """
    检查必填配置是否齐全，缺失时自动生成。
    返回 True 表示配置完整。
    """
    env = _read_env()

    for key, prompt, default, optional in STARTUP_REQUIRED_CONFIGS:
        val = env.get(key, "") or os.environ.get(key, "")
        if not val and not optional:
            if key == "API_KEY":
                val = secrets.token_urlsafe(24)
                _write_env(key, val)
                os.environ[key] = val
                logger.info("[配置] %s 未设置，已自动生成: %s", key, val)
            else:
                logger.warning("[配置] 缺少必填项: %s (%s)", key, prompt)
                return False

    # 重新加载 config 和依赖模块
    import importlib

    import autoteam.config

    importlib.reload(autoteam.config)
    try:
        import autoteam.cloudmail

        importlib.reload(autoteam.cloudmail)
    except Exception:
        pass
    try:
        import autoteam.cloudflare_temp_email

        importlib.reload(autoteam.cloudflare_temp_email)
    except Exception:
        pass
    try:
        import autoteam.mail_provider

        importlib.reload(autoteam.mail_provider)
    except Exception:
        pass

    return True


def _verify_cloudmail(service: dict | None = None):
    """验证 CloudMail 配置是否正确：登录 + 创建测试邮箱 + 删除"""
    service = service or {}
    base_url = str(service.get("base_url") or os.environ.get("CLOUDMAIL_BASE_URL", "") or "").strip()
    email = str(service.get("email") or os.environ.get("CLOUDMAIL_EMAIL", "") or "").strip()
    password = str(service.get("password") or os.environ.get("CLOUDMAIL_PASSWORD", "") or "").strip()
    domain = str(service.get("domain") or os.environ.get("CLOUDMAIL_DOMAIN", "") or "").strip()

    if not all([base_url, email, password, domain]):
        return

    label = get_mail_service_display_name(service or {"type": "cloudmail", "domain": domain})
    logger.info("[验证] %s 配置...", label)

    try:
        from autoteam.cloudmail import CloudMailClient

        client = CloudMailClient(service=service or None)
        client.login()
        logger.info("[验证] %s 登录成功", label)
    except Exception as e:
        logger.error("[验证] %s 登录失败: %s", label, e)
        logger.error("[验证] 请检查 %s 的 base_url / email / password", label)
        return False

    test_account_id = None
    try:
        import uuid as _uuid

        test_account_id, test_email = client.create_temp_email(prefix=f"at-test-{_uuid.uuid4().hex[:6]}")
        logger.info("[验证] %s 创建测试邮箱成功: %s", label, test_email)
    except Exception as e:
        logger.error("[验证] %s 创建邮箱失败: %s", label, e)
        logger.error("[验证] 请检查 %s 的 domain 是否正确", label)
        return False

    try:
        if test_account_id:
            client.delete_account(test_account_id)
            logger.info("[验证] %s 测试邮箱已清理", label)
    except Exception as e:
        logger.warning("[验证] %s 清理测试邮箱失败: %s（不影响使用）", label, e)

    logger.info("[验证] %s 配置验证通过", label)
    return True


def _verify_cloudflare_temp_email(service: dict | None = None):
    """验证 Cloudflare Temp Email 配置是否正确：鉴权 + 创建测试邮箱 + 删除。"""
    service = service or {}
    base_url = str(service.get("base_url") or os.environ.get("CF_TEMP_EMAIL_BASE_URL", "") or "").strip()
    password = str(service.get("admin_password") or os.environ.get("CF_TEMP_EMAIL_ADMIN_PASSWORD", "") or "").strip()
    domain = str(service.get("domain") or os.environ.get("CF_TEMP_EMAIL_DOMAIN", "") or "").strip()

    if not all([base_url, password, domain]):
        return

    label = get_mail_service_display_name(service or {"type": MAIL_PROVIDER_CLOUDFLARE_TEMP_EMAIL, "domain": domain})
    logger.info("[验证] %s 配置...", label)

    try:
        from autoteam.cloudflare_temp_email import CloudflareTempEmailClient

        client = CloudflareTempEmailClient(service=service or None)
        client.login()
        logger.info("[验证] %s 登录成功", label)
    except Exception as e:
        logger.error("[验证] %s 登录失败: %s", label, e)
        logger.error("[验证] 请检查 %s 的 base_url / admin_password", label)
        return False

    test_account_id = None
    try:
        import uuid as _uuid

        test_account_id, test_email = client.create_temp_email(prefix=f"at-test-{_uuid.uuid4().hex[:6]}")
        logger.info("[验证] %s 创建测试邮箱成功: %s", label, test_email)
    except Exception as e:
        logger.error("[验证] %s 创建邮箱失败: %s", label, e)
        logger.error("[验证] 请检查 %s 的 domain 是否正确", label)
        return False

    try:
        if test_account_id:
            client.delete_account(test_account_id)
            logger.info("[验证] %s 测试邮箱已清理", label)
    except Exception as e:
        logger.warning("[验证] %s 清理测试邮箱失败: %s（不影响使用）", label, e)

    logger.info("[验证] %s 配置验证通过", label)
    return True


def _verify_mail_provider(provider: str | None = None):
    default_service = get_default_mail_service()
    if default_service:
        return _verify_mail_service(default_service)

    resolved = provider or get_mail_provider_name()
    if resolved == MAIL_PROVIDER_CLOUDFLARE_TEMP_EMAIL:
        return _verify_cloudflare_temp_email()
    return _verify_cloudmail()


def _verify_mail_service(service: dict | None):
    service = service or {}
    provider = service.get("type")
    if provider == MAIL_PROVIDER_CLOUDFLARE_TEMP_EMAIL:
        return _verify_cloudflare_temp_email(service)
    return _verify_cloudmail(service)


def _verify_mail_services(services: list[dict] | None = None):
    items = services if services is not None else get_mail_services()
    for service in items:
        missing = get_mail_service_missing_fields(service)
        if missing:
            return False
        if not _verify_mail_service(service):
            return False
    return True


def _verify_cpa():
    """验证 CPA 配置是否正确：获取认证文件列表"""
    cpa_url = os.environ.get("CPA_URL", "")
    cpa_key = os.environ.get("CPA_KEY", "")

    if not cpa_url or not cpa_key:
        return True  # 没配就跳过

    logger.info("[验证] CPA 配置...")

    try:
        import requests

        resp = requests.get(
            f"{cpa_url}/v0/management/auth-files",
            headers={"Authorization": f"Bearer {cpa_key}"},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            count = len(data.get("files", []))
            logger.info("[验证] CPA 连接成功（当前 %d 个认证文件）", count)
            return True
        if resp.status_code == 401:
            logger.error("[验证] CPA 连接失败: 密钥无效 (401)")
            logger.error("[验证] 请检查 CPA_KEY 是否正确")
            return False
        logger.error("[验证] CPA 连接失败: HTTP %d", resp.status_code)
        logger.error("[验证] 请检查 CPA_URL 是否正确")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("[验证] CPA 连接失败: 无法连接到 %s", cpa_url)
        logger.error("[验证] 请检查 CPA_URL 是否正确，CPA 服务是否已启动")
        return False
    except Exception as e:
        logger.error("[验证] CPA 连接失败: %s", e)
        return False



