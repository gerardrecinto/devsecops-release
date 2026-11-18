"""Policy checks on the compiled Bicep and on the pipeline files. Needs the bicep CLI for the first group."""
import json
import os
import shutil
import subprocess

import pytest
import yaml

ROOT = os.path.join(os.path.dirname(__file__), "..")
bicep = shutil.which("bicep")


def compiled(path):
    out = subprocess.run([bicep, "build", os.path.join(ROOT, path), "--stdout"], check=True, capture_output=True, text=True)
    return json.loads(out.stdout)


def resources(doc):
    return doc["resources"].values() if isinstance(doc["resources"], dict) else doc["resources"]


@pytest.mark.skipif(bicep is None, reason="bicep CLI not installed")
def test_every_nsg_ends_in_deny_all_inbound():
    doc = compiled("bicep/modules/nsg.bicep")
    deny = doc["variables"]["denyAll"]
    assert deny["name"] == "deny-all-inbound"
    assert deny["properties"]["access"] == "Deny" and deny["properties"]["direction"] == "Inbound"
    assert deny["properties"]["priority"] == 4096
    nsg = next(r for r in resources(doc) if r["type"] == "Microsoft.Network/networkSecurityGroups")
    rules = nsg["properties"]["securityRules"]
    assert rules.endswith("variables('denyAll')))]"), "deny-all must be the last rule"


@pytest.mark.skipif(bicep is None, reason="bicep CLI not installed")
def test_storage_is_private_and_modern():
    doc = compiled("bicep/main.bicep")
    st = next(r for r in resources(doc) if r["type"] == "Microsoft.Storage/storageAccounts")
    p = st["properties"]
    assert p["publicNetworkAccess"] == "Disabled" and p["allowBlobPublicAccess"] is False
    assert p["minimumTlsVersion"] == "TLS1_2" and p["allowSharedKeyAccess"] is False


def load(name):
    with open(os.path.join(ROOT, name)) as f:
        return yaml.safe_load(f)


def test_pipeline_has_manual_gates_for_staging_and_prod():
    ci = load(".gitlab-ci.yml")
    incs = [i for i in ci["include"] if i["local"].endswith("promote.yml")]
    manual = {i["inputs"]["environment"]: i["inputs"]["manual"] for i in incs}
    assert manual == {"dev": False, "test": False, "staging": True, "prod": True}


def test_every_component_declares_inputs_and_a_stage():
    for name in ("bicep", "terraform", "scan", "promote"):
        with open(os.path.join(ROOT, "templates", f"{name}.yml")) as f:
            spec, body = list(yaml.safe_load_all(f))
        assert "inputs" in spec["spec"]
        assert "stage" in spec["spec"]["inputs"]
        assert all("stage" in job for job in body.values())


def test_no_secrets_or_latest_tags_in_templates():
    for name in os.listdir(os.path.join(ROOT, "templates")):
        text = open(os.path.join(ROOT, "templates", name)).read()
        assert ":latest" not in text
