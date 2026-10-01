# Repeatable prototype engineering pipeline

## Goal

The user interacts through ChatGPT. GitHub stores the authoritative design state. A private Windows runner executes deterministic CAD generation and verification. Results return to the same GitHub design branch as machine-readable evidence and a readable report.

No GitHub Actions are used.

## Normal design loop

1. ChatGPT reads `main` and the latest evidence.
2. ChatGPT creates `prototype/<job-id>` from `main`.
3. ChatGPT makes the smallest requested design change on that branch.
4. ChatGPT adds `jobs/<job-id>.json` with `status: queued`.
5. The local daemon discovers the branch and runs `prototype_runner/pipeline.py`.
6. The runner regenerates exports, inspects components, evaluates requirements, and writes evidence.
7. The runner marks the job completed/failed and pushes only to the same prototype branch.
8. ChatGPT reviews `evidence/latest/summary.json` and the diff.
9. If evidence is acceptable, ChatGPT merges the branch. If not, ChatGPT revises it and queues another job.

## Stable contracts

### Component contract

Each component listed in `prototype.yaml` exposes:

- an exporter function that regenerates derived artifacts;
- an inspector function returning deterministic metrics as a Python dictionary.

This allows any future CAD implementation to participate without changing the evidence engine.

### Requirement contract

`requirements/requirements.yaml` maps a component metric to an operator and target. Supported operators are `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, and `between`.

Missing metrics become `UNKNOWN`; they are never silently treated as passes.

### Evidence contract

Every run produces:

- `evidence/runs/<job-id>/summary.json`
- `evidence/runs/<job-id>/report.html`
- `evidence/latest/*`
- `docs/evidence/*` for browser viewing

The JSON includes provenance, metrics, requirement results, assumptions, risks, and component errors.

## One-time Windows bootstrap

After this pipeline is merged to `main`, run `scripts/install_runner.ps1` once on the Windows workstation that will execute CAD/simulation jobs. It creates an isolated clone under `%LOCALAPPDATA%`, installs Python dependencies, and registers a logon Scheduled Task.

The runner requires normal GitHub push authentication on that machine. After bootstrap, normal design requests can originate entirely from ChatGPT.

## Extension points

Future solvers should not replace this pipeline. Add them as stages that emit metrics into the same evidence model. Examples: tolerance Monte Carlo, CalculiX, Project Chrono, DEME, OpenModelica, electronics checks, or other domain solvers.
