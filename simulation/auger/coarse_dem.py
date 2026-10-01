from __future__ import annotations

import json
import math
from pathlib import Path
from time import perf_counter

import numpy as np
from numba import njit

from cad.auger import (
    BARREL_INNER_DIAMETER_MM,
    DISCHARGE_CENTER_X_MM,
    DISCHARGE_CLEAR_DIAMETER_MM,
    FLIGHT_LENGTH_MM,
    FLIGHT_OUTER_DIAMETER_MM,
    FLIGHT_PITCH_MM,
    FLIGHT_START_X_MM,
    HOUSING_LENGTH_MM,
    INLET_CENTER_X_MM,
)
from cad.hopper import OUTLET_OUTER_DIAMETER

ROOT = Path(__file__).resolve().parents[2]

# Phase 02A is intentionally a reduced-order screen, not the final material model.
# It uses a 2D longitudinal soft-sphere DEM with coarse particles and a moving
# representation of the axial intersections of the helical flight.
G_MM_S2 = 9810.0
PARTICLE_RADIUS_MM = 1.0
PARTICLE_COUNT = 220
NORMAL_STIFFNESS = 35_000.0
NORMAL_DAMPING = 160.0
TANGENTIAL_DAMPING = 80.0
FRICTION_COEFFICIENT = 0.50
COHESION_RANGE_MM = 0.35
TIME_STEP_S = 0.0005

SETTLE_S = 1.0
DRIVEN_S = 7.0
STOP_S = 2.0
SNAPSHOT_DT_S = 0.1

BARREL_RADIUS_MM = BARREL_INNER_DIAMETER_MM / 2.0
BARREL_X0 = 7.0
BARREL_X1 = 73.0
BARREL_Z0 = -BARREL_RADIUS_MM
BARREL_Z1 = BARREL_RADIUS_MM

HOPPER_CENTER_X = INLET_CENTER_X_MM
HOPPER_OUTLET_HALF_MM = (OUTLET_OUTER_DIAMETER - 4.0) / 2.0
HOPPER_CONE_TOP_HALF_MM = 38.0
HOPPER_OUTLET_TOP_Z = 23.0
HOPPER_CONE_TOP_Z = 63.0
HOPPER_TOP_Z = 123.0

DISCHARGE_HALF_MM = DISCHARGE_CLEAR_DIAMETER_MM / 2.0
DISCHARGE_X0 = DISCHARGE_CENTER_X_MM - DISCHARGE_HALF_MM
DISCHARGE_X1 = DISCHARGE_CENTER_X_MM + DISCHARGE_HALF_MM
DISCHARGE_BOTTOM_Z = -25.0

FLIGHT_END_X_MM = FLIGHT_START_X_MM + FLIGHT_LENGTH_MM


@njit
def _closest_segment(px, pz, x1, z1, x2, z2):
    dx = x2 - x1
    dz = z2 - z1
    ll = dx * dx + dz * dz
    if ll < 1e-12:
        return x1, z1
    t = ((px - x1) * dx + (pz - z1) * dz) / ll
    t = max(0.0, min(1.0, t))
    return x1 + t * dx, z1 + t * dz


@njit
def _segment_force(
    px,
    pz,
    vx,
    vz,
    x1,
    z1,
    x2,
    z2,
    wall_vx,
    wall_vz,
    cohesion_accel,
    fx,
    fz,
):
    qx, qz = _closest_segment(px, pz, x1, z1, x2, z2)
    dx = px - qx
    dz = pz - qz
    dist2 = dx * dx + dz * dz

    if dist2 < 1e-16:
        sx = x2 - x1
        sz = z2 - z1
        length = math.sqrt(sx * sx + sz * sz) + 1e-12
        nx = -sz / length
        nz = sx / length
        dist = 0.0
    else:
        dist = math.sqrt(dist2)
        nx = dx / dist
        nz = dz / dist

    if dist < PARTICLE_RADIUS_MM:
        overlap = PARTICLE_RADIUS_MM - dist
        rvx = vx - wall_vx
        rvz = vz - wall_vz
        vn = rvx * nx + rvz * nz
        fn = max(0.0, NORMAL_STIFFNESS * overlap - NORMAL_DAMPING * vn)

        tx = -nz
        tz = nx
        vt = rvx * tx + rvz * tz
        ft = min(FRICTION_COEFFICIENT * fn, TANGENTIAL_DAMPING * abs(vt))
        sign = 1.0 if vt > 0.0 else -1.0

        fx += fn * nx - sign * ft * tx
        fz += fn * nz - sign * ft * tz
    elif dist < PARTICLE_RADIUS_MM + COHESION_RANGE_MM and cohesion_accel > 0.0:
        gap = dist - PARTICLE_RADIUS_MM
        fc = cohesion_accel * (1.0 - gap / COHESION_RANGE_MM)
        fx -= fc * nx
        fz -= fc * nz

    return fx, fz


@njit
def _wall_force(
    vx,
    vz,
    nx,
    nz,
    penetration,
    wall_vx,
    wall_vz,
    fx,
    fz,
):
    if penetration <= 0.0:
        return fx, fz

    rvx = vx - wall_vx
    rvz = vz - wall_vz
    vn = rvx * nx + rvz * nz
    fn = max(0.0, NORMAL_STIFFNESS * penetration - NORMAL_DAMPING * vn)

    tx = -nz
    tz = nx
    vt = rvx * tx + rvz * tz
    ft = min(FRICTION_COEFFICIENT * fn, TANGENTIAL_DAMPING * abs(vt))
    sign = 1.0 if vt > 0.0 else -1.0

    fx += fn * nx - sign * ft * tx
    fz += fn * nz - sign * ft * tz
    return fx, fz


@njit
def _static_domain_forces(px, pz, vx, vz, fx, fz):
    # Hopper/outlet side walls. The bottom throat remains open into the barrel.
    if pz >= BARREL_Z1:
        if pz <= HOPPER_OUTLET_TOP_Z:
            half = HOPPER_OUTLET_HALF_MM
            slope = 0.0
        elif pz < HOPPER_CONE_TOP_Z:
            slope = (
                HOPPER_CONE_TOP_HALF_MM - HOPPER_OUTLET_HALF_MM
            ) / (HOPPER_CONE_TOP_Z - HOPPER_OUTLET_TOP_Z)
            half = HOPPER_OUTLET_HALF_MM + slope * (pz - HOPPER_OUTLET_TOP_Z)
        else:
            half = HOPPER_CONE_TOP_HALF_MM
            slope = 0.0

        left = HOPPER_CENTER_X - half
        right = HOPPER_CENTER_X + half

        nlx, nlz = 1.0, slope
        length = math.sqrt(nlx * nlx + nlz * nlz)
        nlx, nlz = nlx / length, nlz / length

        nrx, nrz = -1.0, slope
        length = math.sqrt(nrx * nrx + nrz * nrz)
        nrx, nrz = nrx / length, nrz / length

        fx, fz = _wall_force(
            vx,
            vz,
            nlx,
            nlz,
            (left + PARTICLE_RADIUS_MM) - px,
            0.0,
            0.0,
            fx,
            fz,
        )
        fx, fz = _wall_force(
            vx,
            vz,
            nrx,
            nrz,
            px - (right - PARTICLE_RADIUS_MM),
            0.0,
            0.0,
            fx,
            fz,
        )

        if pz > HOPPER_TOP_Z - PARTICLE_RADIUS_MM:
            fx, fz = _wall_force(
                vx,
                vz,
                0.0,
                -1.0,
                pz - (HOPPER_TOP_Z - PARTICLE_RADIUS_MM),
                0.0,
                0.0,
                fx,
                fz,
            )

    # Barrel and discharge chute.
    if pz < BARREL_Z1 + 1.5 * PARTICLE_RADIUS_MM and pz > DISCHARGE_BOTTOM_Z - 2.0:
        if pz >= BARREL_Z0 - 4.0 * PARTICLE_RADIUS_MM:
            fx, fz = _wall_force(
                vx,
                vz,
                1.0,
                0.0,
                (BARREL_X0 + PARTICLE_RADIUS_MM) - px,
                0.0,
                0.0,
                fx,
                fz,
            )
            fx, fz = _wall_force(
                vx,
                vz,
                -1.0,
                0.0,
                px - (BARREL_X1 - PARTICLE_RADIUS_MM),
                0.0,
                0.0,
                fx,
                fz,
            )

            if px < HOPPER_CENTER_X - 6.2 or px > HOPPER_CENTER_X + 6.2:
                fx, fz = _wall_force(
                    vx,
                    vz,
                    0.0,
                    -1.0,
                    pz - (BARREL_Z1 - PARTICLE_RADIUS_MM),
                    0.0,
                    0.0,
                    fx,
                    fz,
                )

        if px < DISCHARGE_X0 or px > DISCHARGE_X1:
            fx, fz = _wall_force(
                vx,
                vz,
                0.0,
                1.0,
                (BARREL_Z0 + PARTICLE_RADIUS_MM) - pz,
                0.0,
                0.0,
                fx,
                fz,
            )
        elif pz < BARREL_Z0 + PARTICLE_RADIUS_MM:
            fx, fz = _wall_force(
                vx,
                vz,
                1.0,
                0.0,
                (DISCHARGE_X0 + PARTICLE_RADIUS_MM) - px,
                0.0,
                0.0,
                fx,
                fz,
            )
            fx, fz = _wall_force(
                vx,
                vz,
                -1.0,
                0.0,
                px - (DISCHARGE_X1 - PARTICLE_RADIUS_MM),
                0.0,
                0.0,
                fx,
                fz,
            )

    return fx, fz


@njit
def _simulate(pos0, rpm, cohesion_to_weight):
    count = pos0.shape[0]
    pos = pos0.copy()
    vel = np.zeros((count, 2), np.float64)
    active = np.ones(count, np.uint8)
    entered = np.zeros(count, np.uint8)
    discharged = np.zeros(count, np.uint8)

    total_s = SETTLE_S + DRIVEN_S + STOP_S
    steps = int(total_s / TIME_STEP_S)
    snap_every = max(1, int(SNAPSHOT_DT_S / TIME_STEP_S))
    snap_count = steps // snap_every + 1

    snapshots = np.empty((snap_count, count, 2), np.float32)
    active_snapshots = np.empty((snap_count, count), np.uint8)
    times = np.empty(snap_count, np.float32)
    discharge_times = np.full(count, -1.0, np.float64)

    cohesion_accel = cohesion_to_weight * G_MM_S2
    linear_flight_speed = FLIGHT_PITCH_MM * rpm / 60.0
    stopped_phase = linear_flight_speed * DRIVEN_S

    snap_index = 0
    max_barrel_occupancy = 0

    for step in range(steps + 1):
        now = step * TIME_STEP_S
        if step % snap_every == 0:
            snapshots[snap_index, :, :] = pos
            active_snapshots[snap_index, :] = active
            times[snap_index] = now
            snap_index += 1

        if step == steps:
            break

        if now < SETTLE_S:
            phase = 0.0
            flight_velocity = 0.0
        elif now < SETTLE_S + DRIVEN_S:
            phase = linear_flight_speed * (now - SETTLE_S)
            flight_velocity = linear_flight_speed
        else:
            phase = stopped_phase
            flight_velocity = 0.0

        fx = np.zeros(count, np.float64)
        fz = np.zeros(count, np.float64)
        for i in range(count):
            if active[i]:
                fz[i] -= G_MM_S2

        # Soft-sphere particle contacts with a short-range cohesive envelope.
        reach = 2.0 * PARTICLE_RADIUS_MM + COHESION_RANGE_MM
        reach2 = reach * reach
        for i in range(count):
            if not active[i]:
                continue
            for j in range(i + 1, count):
                if not active[j]:
                    continue

                dx = pos[j, 0] - pos[i, 0]
                dz = pos[j, 1] - pos[i, 1]
                dist2 = dx * dx + dz * dz
                if dist2 >= reach2 or dist2 < 1e-16:
                    continue

                dist = math.sqrt(dist2)
                nx = dx / dist
                nz = dz / dist

                if dist < 2.0 * PARTICLE_RADIUS_MM:
                    overlap = 2.0 * PARTICLE_RADIUS_MM - dist
                    rvx = vel[j, 0] - vel[i, 0]
                    rvz = vel[j, 1] - vel[i, 1]
                    vn = rvx * nx + rvz * nz
                    fn = max(
                        0.0,
                        NORMAL_STIFFNESS * overlap - NORMAL_DAMPING * vn,
                    )

                    tx = -nz
                    tz = nx
                    vt = rvx * tx + rvz * tz
                    ft = min(
                        FRICTION_COEFFICIENT * fn,
                        TANGENTIAL_DAMPING * abs(vt),
                    )
                    sign = 1.0 if vt > 0.0 else -1.0

                    pfx = fn * nx - sign * ft * tx
                    pfz = fn * nz - sign * ft * tz
                    fx[i] -= pfx
                    fz[i] -= pfz
                    fx[j] += pfx
                    fz[j] += pfz
                elif cohesion_accel > 0.0:
                    gap = dist - 2.0 * PARTICLE_RADIUS_MM
                    fc = cohesion_accel * (1.0 - gap / COHESION_RANGE_MM)
                    fx[i] += fc * nx
                    fz[i] += fc * nz
                    fx[j] -= fc * nx
                    fz[j] -= fc * nz

        for i in range(count):
            if active[i]:
                fx[i], fz[i] = _static_domain_forces(
                    pos[i, 0],
                    pos[i, 1],
                    vel[i, 0],
                    vel[i, 1],
                    fx[i],
                    fz[i],
                )

        # A longitudinal section of a rotating helix intersects the section in
        # flight lines that advance axially by one pitch per revolution.
        phase_offset = phase % FLIGHT_PITCH_MM
        k0 = int(math.floor((FLIGHT_START_X_MM - phase_offset) / FLIGHT_PITCH_MM)) - 1
        k1 = int(math.ceil((FLIGHT_END_X_MM - phase_offset) / FLIGHT_PITCH_MM)) + 1

        for k in range(k0, k1 + 1):
            x_flight = phase_offset + k * FLIGHT_PITCH_MM
            if x_flight < FLIGHT_START_X_MM or x_flight > FLIGHT_END_X_MM:
                continue

            for i in range(count):
                if not active[i]:
                    continue
                if (
                    pos[i, 1] < BARREL_Z0 + 0.2 * PARTICLE_RADIUS_MM
                    or pos[i, 1] > BARREL_Z1 - 0.2 * PARTICLE_RADIUS_MM
                ):
                    continue

                fx[i], fz[i] = _segment_force(
                    pos[i, 0],
                    pos[i, 1],
                    vel[i, 0],
                    vel[i, 1],
                    x_flight,
                    -7.2,
                    x_flight,
                    7.2,
                    flight_velocity,
                    0.0,
                    cohesion_accel * 0.15,
                    fx[i],
                    fz[i],
                )

        barrel_count = 0
        for i in range(count):
            if not active[i]:
                continue

            vel[i, 0] += fx[i] * TIME_STEP_S
            vel[i, 1] += fz[i] * TIME_STEP_S
            vel[i, 0] *= 0.9995
            vel[i, 1] *= 0.9995

            pos[i, 0] += vel[i, 0] * TIME_STEP_S
            pos[i, 1] += vel[i, 1] * TIME_STEP_S

            if (
                entered[i] == 0
                and BARREL_X0 < pos[i, 0] < BARREL_X1
                and BARREL_Z0 < pos[i, 1] < BARREL_Z1
            ):
                entered[i] = 1

            if (
                BARREL_X0 < pos[i, 0] < BARREL_X1
                and BARREL_Z0 < pos[i, 1] < BARREL_Z1
            ):
                barrel_count += 1

            if (
                pos[i, 1] < DISCHARGE_BOTTOM_Z - 2.0
                and DISCHARGE_X0 - 2.0 < pos[i, 0] < DISCHARGE_X1 + 2.0
            ):
                active[i] = 0
                discharged[i] = 1
                discharge_times[i] = now
            elif pos[i, 0] < -25.0 or pos[i, 0] > 105.0 or pos[i, 1] < -50.0:
                active[i] = 0

        max_barrel_occupancy = max(max_barrel_occupancy, barrel_count)

    return (
        snapshots[:snap_index],
        active_snapshots[:snap_index],
        times[:snap_index],
        discharge_times,
        entered,
        discharged,
        max_barrel_occupancy,
    )


def initial_particles(seed: int = 4) -> np.ndarray:
    rng = np.random.default_rng(seed)
    points: list[list[float]] = []
    spacing = 2.18 * PARTICLE_RADIUS_MM

    for z in np.arange(25.0, 112.0, spacing * 0.92):
        if z < HOPPER_CONE_TOP_Z:
            half = HOPPER_OUTLET_HALF_MM + (
                HOPPER_CONE_TOP_HALF_MM - HOPPER_OUTLET_HALF_MM
            ) * (z - HOPPER_OUTLET_TOP_Z) / (
                HOPPER_CONE_TOP_Z - HOPPER_OUTLET_TOP_Z
            )
        else:
            half = HOPPER_CONE_TOP_HALF_MM

        xs = np.arange(
            HOPPER_CENTER_X - half + 1.2 * PARTICLE_RADIUS_MM,
            HOPPER_CENTER_X + half - 1.2 * PARTICLE_RADIUS_MM,
            spacing,
        )
        if len(points) // 2 % 2:
            xs = xs + 0.7 * PARTICLE_RADIUS_MM

        for x in xs:
            if len(points) >= PARTICLE_COUNT:
                break
            points.append(
                [
                    x + rng.uniform(-0.12, 0.12),
                    z + rng.uniform(-0.10, 0.10),
                ]
            )
        if len(points) >= PARTICLE_COUNT:
            break

    return np.asarray(points[:PARTICLE_COUNT], dtype=np.float64)


def run_case(rpm: float, cohesion_to_weight: float, seed: int = 4):
    start = perf_counter()
    output = _simulate(initial_particles(seed), rpm, cohesion_to_weight)
    runtime_s = perf_counter() - start

    (
        snapshots,
        active_snapshots,
        times,
        discharge_times,
        entered,
        discharged,
        max_barrel_occupancy,
    ) = output

    settle_discharge = np.sum(
        (discharge_times >= 0.0) & (discharge_times < SETTLE_S)
    )
    driven_discharge = np.sum(
        (discharge_times >= SETTLE_S)
        & (discharge_times < SETTLE_S + DRIVEN_S)
    )
    stop_residual = np.sum(discharge_times >= SETTLE_S + DRIVEN_S)

    driven_times = discharge_times[
        (discharge_times >= SETTLE_S)
        & (discharge_times < SETTLE_S + DRIVEN_S)
    ]
    bins = np.arange(SETTLE_S, SETTLE_S + DRIVEN_S + 1e-9, 1.0)
    histogram, _ = np.histogram(driven_times, bins)
    delivery_cv = (
        float(np.std(histogram) / np.mean(histogram))
        if np.mean(histogram) > 0.0
        else None
    )

    metrics = {
        "rpm": rpm,
        "cohesion_to_weight": cohesion_to_weight,
        "particle_count": PARTICLE_COUNT,
        "coarse_particle_diameter_mm": 2.0 * PARTICLE_RADIUS_MM,
        "entered_barrel": int(entered.sum()),
        "discharged_total": int(discharged.sum()),
        "discharged_during_settle": int(settle_discharge),
        "discharged_during_run": int(driven_discharge),
        "stop_residual_particles": int(stop_residual),
        "delivery_bins_particles_per_s": histogram.tolist(),
        "delivery_cv": delivery_cv,
        "max_barrel_occupancy": int(max_barrel_occupancy),
        "runtime_s": runtime_s,
    }

    return metrics, (snapshots, active_snapshots, times)


def animation_payload(metrics, snapshots) -> dict:
    positions, active, times = snapshots
    frames = []
    # Source snapshots are 0.1 s; publish every other one for a compact web asset.
    for frame_index in range(0, len(times), 2):
        particles = [
            [
                round(float(positions[frame_index, i, 0]), 2),
                round(float(positions[frame_index, i, 1]), 2),
            ]
            for i in range(positions.shape[1])
            if active[frame_index, i]
        ]
        frames.append(
            {
                "t_s": round(float(times[frame_index]), 2),
                "particles_xz_mm": particles,
            }
        )

    return {
        "schema_version": 1,
        "simulation": "phase-02a-reduced-order-coarse-dem",
        "scenario_id": "P02A-MEDIUM-60RPM",
        "scenario": metrics,
        "frame_interval_s": 0.2,
        "frames": frames,
    }


def sweep_payload(scenarios: list[dict]) -> dict:
    return {
        "schema_version": 1,
        "simulation": "phase-02a-reduced-order-coarse-dem",
        "component": "auger-meter-v1",
        "status": "MODELLED_UNCALIBRATED",
        "model": {
            "dimension": "2D longitudinal section",
            "contact": (
                "soft-sphere normal spring/dashpot + tangential friction "
                "+ short-range cohesion"
            ),
            "coarse_particle_diameter_mm": 2.0 * PARTICLE_RADIUS_MM,
            "particle_count": PARTICLE_COUNT,
            "friction_coefficient": FRICTION_COEFFICIENT,
            "cohesion_metric": (
                "attractive acceleration / particle weight acceleration"
            ),
            "time_step_s": TIME_STEP_S,
            "settle_s": SETTLE_S,
            "run_s": DRIVEN_S,
            "stop_s": STOP_S,
            "screw_representation": (
                "moving axial intersections of the helical flight"
            ),
        },
        "geometry": {
            "hopper_clear_outlet_mm": OUTLET_OUTER_DIAMETER - 4.0,
            "barrel_inner_diameter_mm": BARREL_INNER_DIAMETER_MM,
            "screw_outer_diameter_mm": FLIGHT_OUTER_DIAMETER_MM,
            "radial_clearance_mm": (
                BARREL_INNER_DIAMETER_MM - FLIGHT_OUTER_DIAMETER_MM
            )
            / 2.0,
            "pitch_mm": FLIGHT_PITCH_MM,
            "discharge_clear_diameter_mm": DISCHARGE_CLEAR_DIAMETER_MM,
        },
        "scenarios": scenarios,
        "interpretation": {
            "control": (
                "At 0 RPM no particles discharged during the driven interval; "
                "transport in this reduced model is caused by screw motion."
            ),
            "baseline": (
                "At 60 RPM and cohesion/weight=0.8, the current screw conveys "
                "most coarse particles but the outlet stream is pulsatile."
            ),
            "cohesion_sensitivity": (
                "Delivery becomes increasingly burst-like as cohesion rises."
            ),
            "confidence": "SCREENING_ONLY_UNCALIBRATED",
        },
        "limitations": [
            "2D longitudinal reduction, not full 3D DEM.",
            (
                "2 mm coarse grains represent groups of much finer real "
                "rangoli particles."
            ),
            (
                "Cohesion values are dimensionless screening envelopes, not "
                "measured material properties."
            ),
            (
                "No rolling resistance, electrostatics, air entrainment or "
                "humidity model."
            ),
            (
                "Mass flow in g/s is intentionally not reported until "
                "calibration/full 3D DEM."
            ),
        ],
    }


def main() -> None:
    scenario_specs = [
        (0.0, 0.8),
        (30.0, 0.8),
        (60.0, 0.15),
        (60.0, 0.8),
        (60.0, 2.0),
        (60.0, 5.0),
    ]

    scenarios = []
    baseline_snapshots = None
    baseline_metrics = None

    for rpm, cohesion in scenario_specs:
        metrics, snapshots = run_case(rpm, cohesion)
        scenarios.append(metrics)
        if rpm == 60.0 and cohesion == 0.8:
            baseline_metrics = metrics
            baseline_snapshots = snapshots

    results_dir = ROOT / "simulation" / "auger" / "results"
    published_dir = ROOT / "docs" / "simulation" / "auger"
    results_dir.mkdir(parents=True, exist_ok=True)
    published_dir.mkdir(parents=True, exist_ok=True)

    sweep = sweep_payload(scenarios)
    animation = animation_payload(baseline_metrics, baseline_snapshots)

    (results_dir / "phase-02a-coarse-dem-sweep.json").write_text(
        json.dumps(sweep, indent=2) + "\n",
        encoding="utf-8",
    )
    compact_animation = json.dumps(animation, separators=(",", ":")) + "\n"
    (results_dir / "phase-02a-medium-60rpm-animation.json").write_text(
        compact_animation,
        encoding="utf-8",
    )
    (published_dir / "phase-02a-medium-60rpm.json").write_text(
        compact_animation,
        encoding="utf-8",
    )

    print(json.dumps(sweep, indent=2))


if __name__ == "__main__":
    main()
