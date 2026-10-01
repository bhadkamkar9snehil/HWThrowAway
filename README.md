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

The enhanced viewer supports orbit, pan, zoom, front/right/top/isometric views, wireframe, transparency, grid/axes, auto-rotate, part visibility, and part selection. It is already structured for multiple components later.

## Repeatable prototype pipeline

This repo now includes a solver-independent engineering pipeline. ChatGPT creates an isolated `prototype/*` branch and queues a job; a private Windows runner regenerates the CAD, measures deterministic metrics, evaluates machine-readable requirements, publishes evidence, and pushes the result back to that same branch. The runner never pushes directly to `main` and no GitHub Actions are used.

The stable design contracts are:

- `prototype.yaml` — project/components and their exporter/inspector entry points
- `requirements/requirements.yaml` — executable acceptance criteria
- `architecture/interfaces.yaml` — interfaces between components
- `assumptions/` and `risks/` — explicit uncertainty rather than hidden claims
- `prototype_runner/` — deterministic pipeline and GitHub branch daemon
- `evidence/` + `docs/evidence/` — machine-readable and browser-readable proof

See [PIPELINE.md](PIPELINE.md) for the exact chat → branch → runner → evidence → merge loop.

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
  pipeline.py                       CAD/check/evidence runner
  daemon.py                         Watches remote prototype/* branches
requirements/                       Executable requirements
architecture/                       Interface contracts
assumptions/                        Explicit assumptions
risks/                              Explicit risks
jobs/                               Chat/runner job handoff
scripts/install_runner.ps1          One-time Windows daemon installer

.agents/skills/
  mechanical-product-design/
    SKILL.md                         Mechanical design + assembly workflow

AGENTS.md                            Repo-wide instructions for coding agents
```

## Regenerate the model manually

```bash
pip install -r requirements.txt
python cad/hopper.py
```

Run the complete digital evidence pipeline:

```bash
python prototype_runner/pipeline.py
```

The SVG is not an AI illustration. It is a geometric projection generated directly from the same CadQuery solid used for the STEP/STL outputs.

## Reusable CAD viewer setup guide

For setting up another GitHub repository with the same browser-based interactive CAD viewing pattern, see [CAD_VIEWER_HANDOVER.md](CAD_VIEWER_HANDOVER.md). It covers repository layout, STEP/STL/GLB roles, Three.js viewer architecture, model discovery, GitHub Pages configuration, deployment verification, troubleshooting, and a handoff prompt for another agent.

## Design rule

Keep the model parametric. Dimensions and mating/interface decisions belong in source code; STL is an output, not the editable source.
