# Agent instructions — Rangoli Printer Prototype

This repository is for a physical mechanical prototype. Treat geometry as engineering geometry, not decorative 3D art.

Before creating or changing mechanical parts, read and follow:

- `skills/mechanical-product-design/SKILL.md`

Project conventions:

- Use millimetres unless explicitly stated otherwise.
- CadQuery Python is the source of truth for parametric geometry.
- Preserve the smallest sufficient change; do not add mechanisms or features the user did not request.
- Every physical component must have a clear function, interfaces, assembly method, and manufacturing route.
- For mating parts, explicitly define datum/interface dimensions and clearances rather than relying on visual alignment.
- Before finalizing an assembly change, check interference, access for assembly/disassembly, motion clearance, wall thickness, and manufacturability.
- Generated artifacts should include STEP for engineering exchange, STL for printing/viewing, and an SVG preview when useful.
- Keep `docs/models.json` current so the browser viewer represents the latest committed geometry.
- Do not add GitHub Actions. Generated files are updated explicitly when CAD source changes.
