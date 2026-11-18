"""The Pages demo runs the same rules in JavaScript. Keep it honest."""
import json
import os
import re
import shutil
import subprocess

import pytest

from deploytriage import rules
from deploytriage.triage import triage

ROOT = os.path.join(os.path.dirname(__file__), "..")
PAGE = os.path.join(ROOT, "docs", "index.html")
FIX = os.path.join(ROOT, "tests", "fixtures")


def test_page_embeds_the_current_rules():
    html = open(PAGE).read()
    embedded = json.loads(re.search(r"const TRIAGE=(.*?);\nconst SAMPLES", html, re.S).group(1))
    assert embedded["rules"] == [list(r) for r in rules.RULES]
    assert embedded["wrapper"] == list(rules.WRAPPER)


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_js_matches_python_on_every_fixture():
    out = subprocess.run(["node", os.path.join(ROOT, "tests", "page_parity.js"), PAGE, FIX],
                         check=True, capture_output=True, text=True).stdout
    js = json.loads(out)
    assert js
    for name, (layer, also) in js.items():
        py = triage(open(os.path.join(FIX, name)).read())
        assert (layer, also) == (py["layer"], py["also"]), name
