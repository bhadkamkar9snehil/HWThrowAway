# Auger Meter V1 — Phase 01 Validation

Executed in the ChatGPT tool environment with CadQuery 2.8.0.

## Executable requirement result

7 / 7 auger requirements pass:

| Requirement | Actual | Result |
|---|---:|---|
| AUG-GEO-001 screw is one solid | 1 | PASS |
| AUG-GEO-002 housing is one solid | 1 | PASS |
| AUG-GEO-003 radial running clearance | 0.40 mm | PASS |
| AUG-INT-001 hopper/socket radial clearance | 0.20 mm | PASS |
| AUG-INT-002 inlet clear diameter | 12.40 mm | PASS |
| AUG-KIN-001 sampled full rotation | true | PASS |
| AUG-GEO-004 discharge clear diameter | 10.00 mm | PASS |

## Additional metrics

- screw OD: 15.2 mm
- barrel ID: 16.0 mm
- shaft: 5.0 mm
- pitch: 10.0 mm
- active screw turns: 6
- housing length: 80.0 mm
- sampled rotation positions: 12 at 30° increments
- maximum sampled screw/housing interference: 0 mm³
- ideal geometric displacement: 1.618234 mL/rev

## Interpretation

This proves the current CAD is internally consistent and can rotate through the housing at the sampled orientations. It does **not** prove rangoli powder flow, torque, dose repeatability, anti-bridging behaviour or stop/dribble performance. Those are Phase 02 DEM outputs.
