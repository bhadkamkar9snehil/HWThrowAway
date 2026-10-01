# Auger Meter V1 — Phase 01 Design Record

Status: **geometry/kinematics baseline complete; powder physics not yet validated**

## Objective
Create a compact single-screw volumetric feeder under the existing rangoli hopper. Phase 01 is limited to geometry, interfaces, printable clearances, bearing/shaft architecture, and collision-free rotation. It does not claim a powder flow rate yet.

## Inputs inherited from the current hopper
- Hopper outlet outside diameter: 16.0 mm.
- Hopper outlet clear diameter: 12.0 mm.
- Fine rangoli powder; particle-size distribution, bulk density, wall friction, cohesion and humidity response are not yet calibrated.

## Concept decision
A **single horizontal metering screw in a close-clearance barrel** is the baseline.

Why: deterministic displacement per revolution, compact package, reversible/start-stop capable, straightforward to print, and directly testable later in DEM. An inlet agitator can be added without replacing the metering core.

Deferred alternatives:
- rotary pocket/star wheel — simpler but weaker sealing/dose resolution for fine powder;
- vibratory feed — useful for flow assistance but harder to stop cleanly;
- twin screw — stronger for cohesive powders, but more complex; promote only if single-screw DEM shows unstable fill/bridging.

## Baseline geometry
| Parameter | V1 |
|---|---:|
| Screw flight OD | 15.2 mm |
| Barrel ID | 16.0 mm |
| Radial running clearance | 0.40 mm |
| Shaft | 5.0 mm |
| Flight pitch | 10.0 mm |
| Flight thickness | 1.2 mm |
| Active flight length | 60.0 mm |
| Turns | 6 |
| Housing length | 80.0 mm |
| Hopper socket ID | 16.4 mm |
| Nominal hopper/socket radial clearance | 0.20 mm |
| Inlet clear diameter | 12.4 mm |
| Downward discharge clear diameter | 10.0 mm |
| Bearings | 625 envelope, 5 × 16 × 5 mm |
| Bearing pocket | 16.15 mm × 5.2 mm deep |

The 5 mm shaft matches common compact bearings and 5-to-5 mm motor couplers. Bearing seats sit outside the powder cavity with internal shoulders.

## Phase 01 evidence
- Screw is one valid solid.
- Housing is one valid solid.
- Radial screw/barrel clearance is 0.40 mm.
- Hopper interface preserves the current 16 mm OD / 12 mm clear outlet.
- 12 sampled screw orientations over 360° show 0 mm³ interference with the housing.
- Ideal geometric swept displacement is 1.618234 mL/rev.

The displacement is geometric only, **not** a powder-delivery prediction.

## Still unproven
Mass/rev, dose CV, torque, bridging, compaction/caking, stop dribble, humidity effects, real printed fits, bearing contamination and wear.

## Phase plan
### Phase 01 — Geometry + kinematics
Implemented now: screw, barrel, hopper socket, downward discharge, bearing interfaces, nominal fit and sampled collision-free rotation.

### Phase 02 — Granular simulation
Add DEM for the hopper throat + screw. Sweep RPM and uncertain powder properties. Measure throughput, mass/rev, torque, fill fraction, bridging and stop residual.

### Phase 03 — Robust geometry search
Sweep pitch, radial clearance, inlet geometry and discharge diameter. Prefer geometry stable over a broad powder-property envelope rather than one tuned to one assumed powder.

### Phase 04 — Physical calibration later
Measure powder properties/dose data, calibrate DEM, and rerun the design envelope.

## Promotion rule
V1 is **geometrically viable**, not yet proven for powder. Promote to **modelled for powder** only after Phase 02, and to **validated** only after later physical calibration.
