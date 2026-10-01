# Auger Meter V1 — Phase 02 DEM Plan

## Simulation status
A true powder/DEM simulation is **not implemented yet**. Phase 01 adds deterministic CAD checks plus a sampled 360° rotational-clearance simulation.

Phase 02 will add granular physics while keeping the same ChatGPT-driven workflow and common evidence format.

## Geometry
Use the committed auger-meter-v1 geometry:
- 15.2 mm screw OD
- 5 mm shaft
- 10 mm pitch
- 16 mm barrel ID
- 12.4 mm inlet
- 10 mm downward discharge

Include enough hopper throat above the inlet to expose bridging/fill instability.

## Powder model inputs
Until measured values exist, sweep broad envelopes and label results MODELLED / UNCALIBRATED:
- particle-size distribution
- bulk density
- particle-particle friction
- particle-wall friction
- rolling resistance
- restitution
- cohesion/adhesion
- electrostatic term only if needed

## First screening variables
- pitch: 8 / 10 / 12 mm
- radial clearance: 0.25 / 0.40 / 0.60 mm
- discharge clear diameter: 8 / 10 / 12 mm
- speed: 10 / 30 / 60 rpm
- material envelope: low / medium / high friction and cohesion

Use a reduced DOE first, then expand around sensitive regions.

## Outputs
- mean flow
- mass delivered per revolution
- coefficient of variation per revolution
- peak and RMS screw torque
- screw fill fraction
- bridging events
- reverse/backflow
- residual discharge after stop
- particle residence time
- solver/timestep/seed provenance

## Acceptance direction
Prefer geometry that does not bridge, has monotonic delivery per revolution, low relative dose variation, useful torque margin, small stop residual, and does not collapse under modest friction/cohesion changes.

Exact limits wait until deposition mass/line-width/travel-speed requirements are defined.


## Update — Phase 02A executed

The reduced-order 2D coarse-grained DEM screen has now been executed and stored in:

- `simulation/auger/results/phase-02a-coarse-dem-sweep.json`
- `analysis/auger/phase-02a-coarse-dem-results.md`

Key finding: the current geometry conveys material, but delivery is already pulsatile in the low/medium cohesion screens and becomes strongly batch-like at high cohesion.

The original parameter sweep now becomes **Phase 02A.2 geometry optimization** using this inexpensive screen.

The higher-fidelity solver stage is renamed **Phase 02B — full 3D granular DEM**. It remains NOT RUN and should use the actual screw/housing mesh plus calibrated material properties before quantitative g/s or torque claims.
