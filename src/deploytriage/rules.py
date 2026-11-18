"""Rules, most specific first. Each: layer, regex, what it means, next step."""
import re

WRAPPER = ("azure", r"DeploymentFailed|InvalidTemplateDeployment|At least one resource deployment operation failed",
           "Azure rejected the deployment. This line is the wrapper, the cause is in the nested error.",
           "Read the nested `code` field below it.")

LAYERS = ("pipeline", "source", "linux", "iac", "azure", "network", "app-config")

RULES = [
    ("pipeline", r"This GitLab CI configuration is invalid|jobs:\S+ config contains unknown keys|'(\S+)' job needs '(\S+)' job, but",
     "The pipeline file is wrong, nothing ran.", "Run the CI lint on the file; check `needs`, `rules` and component `inputs`."),
    ("pipeline", r"Job's log exceeded limit|execution took longer than|stuck or timed out|Runner system failure|no runners? (?:online|available)",
     "The runner, not the code.", "Check runner tags, capacity and the job timeout."),
    ("source", r"CONFLICT \(content\)|merge conflict|fatal: couldn't find remote ref|pathspec .* did not match",
     "The change set is wrong.", "Rebase or fix the ref, then rerun."),
    ("iac", r"\bBCP\d{3}\b|InvalidTemplate\b|Error: Invalid reference|Error: Unsupported argument|Error acquiring the state lock",
     "The template or state, not Azure.", "Run `az bicep build` or `terraform validate` locally; for a lock, find the running apply."),
    ("azure", r"AuthorizationFailed|RequestDisallowedByPolicy|QuotaExceeded|SkuNotAvailable|ResourceGroupNotFound|AuthenticationFailed|AADSTS\d+",
     "Azure refused it: identity, policy or capacity.", "Read the error code. AuthorizationFailed: the deploy identity's role at that scope. RequestDisallowedByPolicy: which policy assignment."),
    ("network", r"Name or service not known|Could not resolve host|no such host|i/o timeout|connection refused|x509: certificate|PrivateEndpoint\w*|dial tcp .*: connect",
     "The path to the service is broken.", "Check DNS (private zone link), NSG and route table on the subnet, and whether the endpoint is approved."),
    ("app-config", r"CrashLoopBackOff|ImagePullBackOff|ErrImagePull|Readiness probe failed|environment variable .* (?:not set|is required)|Back-off restarting failed container",
     "The platform worked; the app did not start.", "`kubectl describe pod`, container logs, and the config or secret it mounts."),
    ("linux", r"No space left on device|Permission denied|command not found|Segmentation fault|OOMKilled|exit code 137",
     "The host or container environment.", "Disk, permissions, missing binary or memory limit on the runner or node."),
]

COMPILED = [(layer, re.compile(rx, re.I), meaning, nxt) for layer, rx, meaning, nxt in RULES]
WRAPPER_RX = re.compile(WRAPPER[1], re.I)
