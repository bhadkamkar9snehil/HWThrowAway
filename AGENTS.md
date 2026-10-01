# Agent instructions — Rangoli Printer Prototype

This repository is for a physical mechanical prototype. Treat geometry as engineering geometry, not decorative 3D art.

Before creating or changing mechanical parts, read and follow:

- `.agents/skills/mechanical-product-design/SKILL.md`

Project conventions:

- Use millimetres unless explicitly stated otherwise.
- CadQuery Python is the source of truth for parametric geometry.
- Preserve the smallest sufficient change; do not add mechanisms or features the user did not request.
- Every physical component must have a clear function and explicit interfaces.
- For mating parts, explicitly define interface dimensions and clearances rather than relying on visual alignment.
- Before finalizing an assembly change, check interference, motion clearance, wall thickness, and relevant manufacturability constraints.
- Generated artifacts should include STEP for engineering exchange, STL for viewing/printing, and an SVG preview when useful.
- Keep `docs/models.json` current so the browser viewer represents the latest committed geometry.
- Do not add GitHub Actions, background daemons, scheduled jobs, or polling infrastructure.

## Repeatable prototype pipeline

ChatGPT is the execution orchestrator for prototype work:

- Work on an isolated `prototype/<iteration>` branch for substantive design changes.
- Update requirements/interfaces/assumptions when the design contract changes.
- Execute `prototype_runner/pipeline.py` directly in the current tool environment.
- Run additional mechanical simulations ad hoc only when they materially answer a design question.
- Do not edit generated evidence to make a design pass.
- Treat `PASS`, `FAIL`, and `UNKNOWN` literally.
- Never convert an unvalidated physical assumption into a pass.
- Review generated evidence before merging a design branch.
- Do not require the user to run local commands for the normal workflow.
