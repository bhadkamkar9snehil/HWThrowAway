---
name: mechanical-product-design
description: Design and revise functional mechanical prototype parts and assemblies in CadQuery, including mating interfaces, fits, clearances, fasteners, motion, manufacturability, and assembly/serviceability. Use for housings, hoppers, brackets, shafts, gates, dispensers, frames, mechanisms, and any change where physical parts must fit or move together.
---

# Mechanical product design

Use this skill when creating or modifying a physical mechanical object or assembly. The goal is a buildable prototype whose parts fit together intentionally, not merely a visually plausible 3D shape.

## Establish design intent before geometry

For each requested part, identify only what is needed for the current scope: its function, material/manufacturing assumption if known, fixed interfaces, moving interfaces and degrees of freedom, meaningful loads, assembly/disassembly path, and which dimensions are fixed versus selectable.

Do not invent unrelated mechanisms. Prefer the smallest sufficient mechanical solution.

## Model parametrically

Use CadQuery Python as the editable source of truth unless the repository specifies otherwise.

- Use millimetres by default.
- Put important dimensions in named parameters near the top of the model.
- Derive dependent dimensions instead of duplicating magic numbers.
- Build around stable datums, axes, and planes.
- Prefer simple inspectable features over unnecessarily clever geometry.
- Keep parts separate when they will be manufactured, cleaned, or serviced separately.
- Treat STL as an output mesh, not the authoritative editable design.

## Design interfaces first

When two components touch or connect, define the interface explicitly before detailing the surrounding shape.

For every interface define the locating geometry/datum, nominal size, clearance or interference, retention method, allowed motion, insertion/removal direction, and tool access when fasteners are used.

Examples: shaft-to-hole, lid-to-body, rail-to-carriage, servo-to-bracket, screw-to-clearance-hole, insert-to-pocket, gate-to-guide, bearing-to-seat, and nozzle-to-hopper.

## Fits and clearances for printed prototypes

Never assume equal nominal CAD dimensions will fit after manufacturing.

For FDM prototype parts, use these only as starting points unless printer/material calibration is known:

- freely sliding faces: about 0.20–0.35 mm clearance per mating side;
- rotating/sliding shafts in printed holes: about 0.25–0.40 mm radial clearance as a starting point;
- snug locating fits: test a small coupon before committing to a large part;
- press fits: use material/printer-specific coupons or manufacturer guidance rather than guessing;
- purchased fasteners, bearings, inserts, motors, and servos: use actual datasheet dimensions and recommended fits.

These are prototype starting values, not universal tolerances. Printer calibration, material, orientation, and hole shrinkage can dominate.

## Fastening and assembly

Prefer reversible assembly for early prototypes. Use standard fasteners where practical, provide screwdriver/hex-key access, avoid accidentally trapped nuts/components, leave room around heads and washers, and make frequently cleaned parts removable without dismantling the whole machine.

For assemblies, define an assembly order and verify no later part blocks an earlier fastener.

## Motion and mechanisms

For moving components, state intended degrees of freedom, constrain unwanted movement, include clearance over full travel, check neighboring parts/cables/fasteners throughout motion, and avoid relying on friction alone unless intentionally designed.

## Structural sanity

Check obvious load paths, thin sections, stress concentrations, unsupported cantilevers, sharp internal corners, screw bosses, mounting ears, center of gravity, tipping risk, and print-layer direction.

Do not perform pseudo-precision structural calculations without real loads and material inputs; flag unknowns.

## Design for FDM prototyping

Unless another process is specified, avoid unnecessary support, prefer self-supporting slopes/chamfers, choose sensible wall thickness for nozzle/perimeters, avoid tiny unsupported features, orient critical mating surfaces deliberately, and split awkward parts when assembly is easier than support removal.

## Powder-handling components

For hoppers, chutes, and fine-powder paths:

- minimize horizontal ledges where powder can accumulate;
- use smooth transitions and avoid abrupt internal steps;
- keep the outlet path short where possible;
- steepen hopper walls when bridging is observed rather than assuming one universal angle works for every powder;
- make powder-contact parts easy to remove and clean;
- avoid hidden crevices that trap different colours;
- treat outlet size and metering as test-driven because flow depends on particle size, humidity, shape, and packing.

Do not add agitators, augers, vibrators, or gates unless requested or a test demonstrates the need.

## Assembly checks before finalizing

For a multi-part change verify: no geometric interference; motion clearance through full travel; tool/fastener access; insertion and removal paths; parameterized critical mating dimensions; intentional clearances; no unintended trapped components; reasonable cleaning/service access; printable watertight meshes; and that STEP/STL correspond to the same source revision.

## Outputs

For each completed revision prefer:

- editable CadQuery `.py` source;
- `.step` engineering solid;
- `.stl` printable/viewable mesh;
- `.svg` geometric preview when useful.

Update `docs/models.json` whenever components or viewer paths change. When reporting a change, state changed parameters and any fit/assembly assumptions still requiring a physical test.
