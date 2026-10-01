# Repeatable prototype engineering pipeline

## Goal

The user interacts only through ChatGPT. GitHub stores the authoritative design state. **ChatGPT's execution environment is the runner.** Each prototype iteration is executed ad hoc when the user asks for it.

There is no daemon, polling loop, scheduled task, GitHub Action, or workstation bootstrap.

## Normal design loop

1. The user asks for a design or change in ChatGPT.
2. ChatGPT reads the current repository state and latest evidence from GitHub.
3. ChatGPT creates an isolated `prototype/<iteration>` branch when a design change is needed.
4. ChatGPT changes the parametric design and, where necessary, the requirements/interfaces/assumptions that define success.
5. ChatGPT materializes the relevant source files into its execution environment.
6. ChatGPT runs `prototype_runner/pipeline.py` directly.
7. The pipeline regenerates CAD outputs, inspects components, evaluates executable requirements, and produces JSON/HTML evidence.
8. ChatGPT runs any additional relevant simulation or analysis ad hoc and folds its result into the engineering assessment.
9. ChatGPT writes the resulting source/evidence back to the design branch and reviews the diff.
10. ChatGPT reports what passed, failed, or remains unknown. A successful iteration can then be merged.

The user does not operate the pipeline.

## Stable contracts

### Component contract

Each component listed in `prototype.yaml` exposes:

- an exporter function that regenerates derived artifacts;
- an inspector function returning deterministic metrics as a Python dictionary.

This allows future components and solvers to participate without changing the interaction model.

### Requirement contract

`requirements/requirements.yaml` maps a component metric to an operator and target. Supported operators are `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, and `between`.

Missing metrics become `UNKNOWN`; they are never silently treated as passes.

### Evidence contract

Every ad-hoc run produces:

- `evidence/runs/<run-id>/summary.json`
- `evidence/runs/<run-id>/report.html`
- `evidence/latest/*`
- `docs/evidence/*` for browser viewing

The evidence records source ref/commit, measured metrics, requirement results, assumptions, risks, and component errors.

## Current scope

The current implementation proves the execution pattern using deterministic CadQuery geometry checks. It is intentionally solver-independent.

Mechanical simulation extensions can be added behind the same evidence contract when a design needs them, for example:

- tolerance and parameter sweeps;
- multibody/kinematic simulation;
- Project Chrono;
- DEM/DEME for granular-material behaviour;
- structural FEA.

Electronics/PCB simulation is not part of the current target scope.

## User interaction

Normal prompts are simply design intents, for example:

- "Make the hopper 1 litre but keep total height below 150 mm."
- "Add a rotary feeder below it and make sure nothing collides through one full revolution."
- "Compare three outlet sizes and tell me which constraints each one passes."
- "Run the current prototype checks and show me what is still unproven."

ChatGPT decides which deterministic checks or simulations are warranted, executes them immediately, and reports the evidence.


## Workbench publishing

The persistent GitHub Pages workbench is part of the prototype state, not a separate manually maintained demo.

- Each pipeline run refreshes `docs/evidence/summary.json`.
- The pipeline also refreshes `docs/models.json` from each component's `viewer_spec()`.
- `docs/index.html` loads both files from the same GitHub Pages origin on every visit, with embedded fallbacks only for resilience.
- Geometry displayed for the current hopper/auger family is generated from the committed parameters in `docs/models.json`.
- Therefore a dimension or component change is not complete until the pipeline has been run and the workbench data has been committed.
