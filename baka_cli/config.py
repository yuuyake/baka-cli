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
    FILE.write_text(json.dumps(cfg, indent=2))
    os.chmod(FILE, 0o600)  # holds tokens
