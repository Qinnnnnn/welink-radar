"""Configuration management for WeLink Radar.

Stores config in ~/.welink-radar/config.json (mirrors WeChat Radar's approach).
Supports environment variable overrides.
"""

import json
import os
from pathlib import Path
from models.schemas import ConfigModel

DATA_DIR = Path(os.environ.get("WELINK_RADAR_DATA_DIR", Path.home() / ".welink-radar"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_PATH = DATA_DIR / "config.json"

_DEFAULT_CONFIG = ConfigModel()


def read_config() -> ConfigModel:
    """Read config from disk, merging with defaults. Creates file if absent."""
    if CONFIG_PATH.exists():
        try:
            stored = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            merged = _DEFAULT_CONFIG.model_dump()
            merged.update({k: v for k, v in stored.items() if k in merged})
            return ConfigModel(**merged)
        except (json.JSONDecodeError, KeyError):
            pass
    # Write defaults on first run (write directly to avoid recursion)
    _write_defaults()
    return _DEFAULT_CONFIG


def _write_defaults() -> None:
    """Write default config to disk without calling read_config."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(_DEFAULT_CONFIG.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_config(patch: ConfigModel | dict) -> ConfigModel:
    """Merge and persist config changes. Returns the updated config."""
    current = read_config()
    patch_data = patch.model_dump() if isinstance(patch, ConfigModel) else patch
    updated_data = current.model_dump()
    updated_data.update({k: v for k, v in patch_data.items() if k in updated_data})
    CONFIG_PATH.write_text(json.dumps(updated_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return ConfigModel(**updated_data)


def config_status() -> dict:
    """Return setup readiness metadata plus current config."""
    config = read_config()
    return {
        "configured": config.setupCompleted and config.privacyConfirmed,
        "config": config.model_dump(),
        "env_checks": {
            "welink_cli_available": _check_welink_cli(),
            "nga_available": _check_nga(),
            "data_dir": str(DATA_DIR),
            "db_path": str(DATA_DIR / "radar.db"),
        },
        "demo_available": True,
    }


def _check_welink_cli() -> bool:
    """Check if welink-cli is installed by running --version."""
    import subprocess
    try:
        result = subprocess.run(
            ["welink-cli", "--version"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _check_nga() -> bool:
    """Check if nga is installed by running --version."""
    import subprocess
    try:
        result = subprocess.run(
            ["nga", "--version"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
