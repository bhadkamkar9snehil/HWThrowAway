# Rangoli Printer Prototype

A personal mechanical prototyping project for dispensing coloured rangoli powder from image-derived colour data.

The CAD source of truth is **CadQuery Python**. Generated STEP/STL/SVG files are committed so the design can be inspected without running CadQuery.

## Current model — hopper shell V1

![Hopper shell preview](previews/rangoli_hopper_shell_v1.svg)

Current dimensions:

- Top outside diameter: **80 mm**
- Straight cylindrical section: **70 mm**
- Funnel section height: **40 mm**
- Outlet outside diameter: **16 mm**
- Outlet length: **15 mm**
- Wall thickness: **2 mm**
- Overall height: **125 mm**

## View it

- [Open the STL in GitHub's built-in 3D viewer](exports/rangoli_hopper_shell_v1.stl)
- [Open/download the STEP model](exports/rangoli_hopper_shell_v1.step)
- Enhanced interactive viewer: `https://bhadkamkar9snehil.github.io/HWThrowAway/` after GitHub Pages is enabled from **main / docs**.

## Chat-driven prototype pipeline

The repository contains a solver-independent digital prototype pipeline. **ChatGPT is the runner**: on each request it reads the current design from GitHub, makes the requested change on an isolated branch, executes the relevant checks/simulations in its tool environment, produces evidence, and writes the result back to GitHub.

There are no scheduled jobs, background services, GitHub Actions, or required workstation runner.

Core contracts:

- `prototype.yaml` — project/components and exporter/inspector entry points
- `requirements/requirements.yaml` — executable acceptance criteria
- `architecture/interfaces.yaml` — component interface definitions
- `assumptions/` and `risks/` — explicit uncertainty
- `prototype_runner/pipeline.py` — deterministic pipeline executable
- `evidence/` + `docs/evidence/` — machine-readable and browser-readable proof

See [PIPELINE.md](PIPELINE.md) for the exact ad-hoc workflow.

## Repository structure

```text
cad/
  hopper.py                         Parametric CadQuery source + metric inspector
exports/
  rangoli_hopper_shell_v1.step      Engineering CAD solid
  rangoli_hopper_shell_v1.stl       Printable / browser-viewable mesh
previews/
  rangoli_hopper_shell_v1.svg       Code-generated projection

docs/
  index.html                        Interactive Three.js viewer
  models.json                       Viewer part manifest
  evidence/                         Latest generated verification report

prototype_runner/
  pipeline.py                       Deterministic CAD/check/evidence pipeline
requirements/                       Executable requirements
architecture/                       Interface contracts
assumptions/                        Explicit assumptions
risks/                              Explicit risks

.agents/skills/
  mechanical-product-design/
    SKILL.md                         Mechanical design + assembly workflow

AGENTS.md                            Repo-wide instructions for coding agents
```

## Pipeline executable

The same executable ChatGPT uses can also be run manually when debugging:

```bash
pip install -r requirements.txt
python prototype_runner/pipeline.py --json
```

Manual execution is optional; the intended user workflow is through ChatGPT.

The SVG is not an AI illustration. It is a geometric projection generated directly from the same CadQuery solid used for the STEP/STL outputs.

## Reusable CAD viewer setup guide

For setting up another GitHub repository with the same browser-based interactive CAD viewing pattern, see [CAD_VIEWER_HANDOVER.md](CAD_VIEWER_HANDOVER.md).

## Design rule

Keep the model parametric. Dimensions and mating/interface decisions belong in source code; STL is an output, not the editable source.
