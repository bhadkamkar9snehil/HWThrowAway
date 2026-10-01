# Phase 02A — Fine Rangoli Powder Screening

## What was actually simulated

A reduced-order **2D coarse-grained discrete-element model** was run against the current hopper + auger geometry. It includes:

- gravity;
- soft-sphere particle contact;
- tangential friction;
- a short-range cohesion term;
- hopper side walls and 12 mm clear throat;
- 16 mm auger barrel;
- 15.2 mm screw envelope with 10 mm pitch;
- 10 mm discharge;
- moving helical-flight intersections;
- 1 s settling, 7 s driven interval and 2 s post-stop interval.

The simulation uses 220 coarse particles of 2 mm diameter. These are numerical coarse grains representing groups of much finer real rangoli particles. They are **not** intended to represent the actual particle size.

## Sanity control

At **0 RPM**, after the initial settling interval, the model discharged **0 particles during the 7 s driven interval**.

That is important: transport in the screening model is coming from the screw motion rather than a model that simply leaks material through the outlet.

## Current-geometry results

| RPM | Cohesion / weight | Driven discharge | Stop residual | Delivery CV |
|---:|---:|---:|---:|---:|
| 0 | 0.8 | 0 / 220 | 0 | n/a |
| 30 | 0.8 | 144 / 220 | 10 | 0.572 |
| 60 | 0.15 | 198 / 220 | 2 | 0.475 |
| 60 | 0.8 | 215 / 220 | 0 | 0.581 |
| 60 | 2.0 | 220 / 220 | 0 | 0.749 |
| 60 | 5.0 | 220 / 220 | 0 | 1.583 |

The delivery CV is the coefficient of variation of the particle count discharged in 1-second bins during the driven interval.

## What this says

1. **The current auger concept conveys material in the reduced model.** The 0 RPM control does not, while 30/60 RPM do.
2. **The current geometry is not yet a convincing precision metering design.** Even the low-cohesion case has a delivery CV of about 0.48.
3. **Cohesion makes the outlet stream strongly burst-like.** In the strongest screening envelope almost all delivery collapses into two large pulses.
4. At 30 RPM the same medium-cohesion case leaves **10 coarse particles discharging after the drive stops**, which is directly relevant to rangoli line endings and corners.
5. No bridging was demonstrated by this reduced model. That should not be interpreted as proof that real fine powder cannot bridge.

## Confidence

**SCREENING / UNCALIBRATED.**

This is useful for concept rejection and sensitivity discovery. It is not sufficient for g/s, motor torque, final dose accuracy, or hardware sizing.

## Why we are not claiming full DEM yet

The execution environment does not currently have Project Chrono DEM/DEME or LAMMPS installed. Phase 02A therefore uses a reproducible in-repo reduced-order DEM rather than inventing full-3D results.

The higher-fidelity next stage should use a full 3D granular solver with the actual screw/barrel mesh and a calibrated powder envelope. Current LAMMPS documentation explicitly includes granular triangular surfaces and a screw-feeder example, making it a good candidate for Phase 02B when the solver is available.

## Next design question

Before increasing fidelity, use this screening model to compare pitch, radial clearance, inlet geometry and discharge diameter. We should look for a geometry whose delivery remains substantially less pulsatile across the cohesion envelope, then carry the survivors into full 3D DEM.
