# devsecops-release-lab

Reusable GitLab CI components, Bicep and Terraform modules for Azure networking, security scan gates, and a tool that reads a failed deploy log and says which layer broke. Checked in CI. Not run on a GitLab server or a live Azure subscription.

[![CI](https://github.com/gerardrecinto/devsecops-release-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/gerardrecinto/devsecops-release-lab/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/github/license/gerardrecinto/devsecops-release-lab)](LICENSE)

**[Live page: paste a failed deploy log](https://gerardrecinto.github.io/devsecops-release-lab/)**

## Run it

Python 3.10 or newer. Node and Docker only for the last line.

```bash
git clone https://github.com/gerardrecinto/devsecops-release-lab
cd devsecops-release-lab
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
python -m deploytriage tests/fixtures/azure_auth_wrapped.log
npx gitlab-ci-local --list
```

The triage tool prints the layer, the first failure, what it means and what to check next. The Bicep tests need the `bicep` CLI and skip without it.

## What is here

| Part | Where | Checked how |
| :--- | :--- | :--- |
| GitLab CI components with typed inputs | `templates/` | parsed and run with `gitlab-ci-local` in CI; a test checks every component declares inputs and a stage |
| Four-environment pipeline, manual gates on staging and prod | `.gitlab-ci.yml` | `gitlab-ci-local --list` shows staging and prod as manual; a test asserts it |
| Azure spoke network in Bicep | `bicep/` | `bicep lint` with zero output, `build-params` for dev, test, staging, prod |
| Policy as tests on the compiled Bicep | `tests/test_invariants.py` | every NSG ends in deny-all-inbound; storage is private, TLS 1.2, no shared keys |
| Terraform VNet module | `terraform/modules/vnet` | `terraform test` with a mocked provider |
| Secret and IaC scans | `templates/scan.yml` | Gitleaks and Checkov pass in CI |
| Deploy triage | `src/deploytriage` | 8 representative logs, Azure wrapper errors, a page that runs the same rules in JavaScript and a test that compares them |

## Trade-offs

All design-only; nothing here ran in production.

| Chose | Over | Costs | Flip when |
| :--- | :--- | :--- | :--- |
| Components with typed inputs | Copied YAML | A team maintains them | One project, no reuse |
| Private endpoint plus private DNS | Service endpoint | Per-endpoint cost, DNS to get right | A firewall rule is enough |
| Mocked-provider tests | Integration tests | Miss provider and API behaviour | The risk is in the real API |
| Manual gate on staging and prod | Fully automatic | A pipeline can sit blocked | Health-gated rollback is trusted |
| Rules in the triage tool | A model | Misses new messages | Enough labelled logs to measure a classifier |

## Not covered

- No GitLab server. The pipeline jobs ran under `gitlab-ci-local` (real containers, no GitLab runner or API). Components are a local include, not a catalog release.
- No live Azure. Bicep was linted and built, Terraform was tested with a mocked provider. Nothing was deployed or planned against a subscription.
- No Azure Government, no DoD controls, no STIG work.
- The deploy job compiles parameters and prints; it only calls Azure when `AZURE_CLIENT_ID` and an ID token exist.
- The sample logs are representative messages, not captured from a real run.
- Scans are Gitleaks and Checkov. No SAST or container scan here; Trivy runs in [gitops-aks-demo](https://github.com/gerardrecinto/gitops-aks-demo).

MIT license.
