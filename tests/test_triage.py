import os

import pytest

from deploytriage.triage import triage

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def read(name):
    return open(os.path.join(FIX, name)).read()


@pytest.mark.parametrize("name,layer", [
    ("pipeline_invalid.log", "pipeline"),
    ("runner_timeout.log", "pipeline"),
    ("bicep_error.log", "iac"),
    ("tf_lock.log", "iac"),
    ("azure_auth_wrapped.log", "azure"),
    ("dns_private_endpoint.log", "network"),
    ("crashloop.log", "app-config"),
    ("disk_full.log", "linux"),
])
def test_layer(name, layer):
    assert triage(read(name))["layer"] == layer


def test_wrapper_line_does_not_hide_the_cause():
    res = triage("DeploymentFailed: At least one resource deployment operation failed\nAuthorizationFailed on scope x\n")
    assert res["layer"] == "azure" and "AuthorizationFailed" in res["evidence"]


def test_wrapper_alone_is_reported_as_wrapper():
    res = triage("InvalidTemplateDeployment: the template deployment failed\n")
    assert "wrapper" in res["meaning"]


def test_first_failure_wins_and_others_are_listed():
    res = triage("Could not resolve host: x\nCrashLoopBackOff\n")
    assert res["layer"] == "network" and res["also"] == ["app-config"]


def test_unknown_log_points_at_the_first_error():
    assert triage("all fine\n")["layer"] == "unknown"
