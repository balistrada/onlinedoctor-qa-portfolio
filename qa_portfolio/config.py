"""Resolve which environment the suite talks to."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENTS_FILE = ROOT / "config" / "environments.yml"
REQUIREMENTS_FILE = ROOT / "requirements" / "catalog.yml"
DEFECTS_FILE = ROOT / "defects" / "register.yml"

USER_AGENT = (
    "VeryOpsQAPortfolio/1.0 "
    "(read-only portfolio; +https://github.com/balistrada/onlinedoctor-qa-portfolio)"
)


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a mapping")
    return data


def load_environments() -> dict:
    return load_yaml(ENVIRONMENTS_FILE)


def resolve_base_url() -> str:
    """BASE_URL wins. Otherwise TEST_ENV (default prod) selects a profile."""
    override = os.environ.get("BASE_URL", "").strip()
    if override:
        url = override.rstrip("/")
    else:
        name = os.environ.get("TEST_ENV", "prod").strip() or "prod"
        environments = load_environments()
        if name not in environments:
            known = ", ".join(sorted(environments))
            raise KeyError(f"Unknown TEST_ENV {name!r}. Known: {known}")
        url = str(environments[name]["base_url"]).rstrip("/")
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"BASE_URL is not an absolute http(s) URL: {url}")
    if parsed.username or parsed.password:
        raise ValueError("BASE_URL must not carry credentials")
    return url


def host_of(url: str) -> str:
    return urlparse(url).netloc
