import json
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).parent


def load(name):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def cases(name, key):
    """Turn a list of dicts from a JSON file into pytest params, using each case's 'id'."""
    return [pytest.param(c, id=c["id"]) for c in load(name)[key]]
