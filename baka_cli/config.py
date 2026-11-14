import json
import os
from pathlib import Path

BASE = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
DIR = BASE / "baka-cli"
FILE = DIR / "config.json"
OLD = BASE / "techno-cli" / "config.json"  # from before the rename, still read once


def load():
    for f in (FILE, OLD):
        try:
            return json.loads(f.read_text())
        except Exception:
            continue
    return {}


def save(cfg):
    DIR.mkdir(parents=True, exist_ok=True)
    tmp = DIR / f".config.{os.getpid()}.tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(cfg, indent=2))
        os.replace(tmp, FILE)
    except Exception:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise
