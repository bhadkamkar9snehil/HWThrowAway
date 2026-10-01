from __future__ import annotations

from pathlib import Path
import math

import cadquery as cq

MODEL_ID = "auger-meter-v1"

# Single-screw volumetric metering core for fine rangoli powder.
# Geometry/kinematics are verified here; powder-flow performance is not claimed
# until the DEM phase is implemented and material parameters are calibrated.

SHAFT_DIAMETER_MM = 5.0
SHAFT_HOLE_DIAMETER_MM = 5.7

FLIGHT_OUTER_DIAMETER_MM = 15.2
FLIGHT_PITCH_MM = 10.0
FLIGHT_THICKNESS_MM = 1.2
FLIGHT_ROOT_OVERLAP_MM = 0.25
FLIGHT_START_X_MM = 10.0
FLIGHT_LENGTH_MM = 60.0

BARREL_INNER_DIAMETER_MM = 16.0
BARREL_OUTER_DIAMETER_MM = 22.0
HOUSING_LENGTH_MM = 80.0
PROCESS_CAVITY_START_X_MM = 7.0
PROCESS_CAVITY_END_X_MM = 73.0

INLET_CENTER_X_MM = 22.0
INLET_CLEAR_DIAMETER_MM = 12.4
HOPPER_SOCKET_INNER_DIAMETER_MM = 16.4
HOPPER_SOCKET_OUTER_DIAMETER_MM = 22.0
HOPPER_SOCKET_HEIGHT_MM = 10.0

DISCHARGE_CENTER_X_MM = 64.0
DISCHARGE_CLEAR_DIAMETER_MM = 10.0
DISCHARGE_OUTER_DIAMETER_MM = 14.0
DISCHARGE_LENGTH_MM = 15.0

# 625 bearing envelope: 5 x 16 x 5 mm.
BEARING_NOMINAL_ID_MM = 5.0
BEARING_NOMINAL_OD_MM = 16.0
BEARING_NOMINAL_WIDTH_MM = 5.0
BEARING_POCKET_DIAMETER_MM = 16.15
BEARING_POCKET_DEPTH_MM = 5.2

MOTOR_SIDE_SHAFT_EXTENSION_MM = 15.0
OUTBOARD_SHAFT_EXTENSION_MM = 5.0

# Existing hopper interface from cad/hopper.py.
HOPPER_OUTLET_OUTER_DIAMETER_MM = 16.0
HOPPER_OUTLET_CLEAR_DIAMETER_MM = 12.0

ROTATION_SAMPLE_DEGREES = 30


def _cylinder_x(diameter_mm: float, length_mm: float, x0_mm: float = 0.0) -> cq.Workplane:
    return (
        cq.Workplane("YZ", origin=(x0_mm, 0, 0))
        .circle(diameter_mm / 2.0)
        .extrude(length_mm)
    )


def build_flight() -> cq.Workplane:
    """Build the helical flight as a true swept solid."""
    outer_radius = FLIGHT_OUTER_DIAMETER_MM / 2.0
    root_radius = SHAFT_DIAMETER_MM / 2.0 - FLIGHT_ROOT_OVERLAP_MM
    mid_radius = (outer_radius + root_radius) / 2.0

    # Build around Z, then rotate the finished flight so the auger axis is +X.
    helix = cq.Wire.makeHelix(
        FLIGHT_PITCH_MM,
        FLIGHT_LENGTH_MM,
        mid_radius,
    )
    tangent = (0, mid_radius, FLIGHT_PITCH_MM / (2.0 * math.pi))
    profile_plane = cq.Plane(
        origin=(mid_radius, 0, 0),
        xDir=(1, 0, 0),
        normal=tangent,
    )
    flight = (
        cq.Workplane(profile_plane)
        .rect(outer_radius - root_radius, FLIGHT_THICKNESS_MM)
        .sweep(helix, isFrenet=True, combine=False)
    )
    return (
        flight
        .rotate((0, 0, 0), (0, 1, 0), 90)
        .translate((FLIGHT_START_X_MM, 0, 0))
    )


def build_screw() -> cq.Workplane:
    total_shaft_length = (
        HOUSING_LENGTH_MM
        + MOTOR_SIDE_SHAFT_EXTENSION_MM
        + OUTBOARD_SHAFT_EXTENSION_MM
    )
    shaft = _cylinder_x(
        SHAFT_DIAMETER_MM,
        total_shaft_length,
        -MOTOR_SIDE_SHAFT_EXTENSION_MM,
    )
    return shaft.union(build_flight()).clean()


def build_housing() -> cq.Workplane:
    outer = _cylinder_x(BARREL_OUTER_DIAMETER_MM, HOUSING_LENGTH_MM)
    process_bore = _cylinder_x(
        BARREL_INNER_DIAMETER_MM,
        PROCESS_CAVITY_END_X_MM - PROCESS_CAVITY_START_X_MM,
        PROCESS_CAVITY_START_X_MM,
    )
    housing = outer.cut(process_bore)

    # Bearing pockets enter from the outside, leaving internal shoulders between
    # the bearings and powder cavity.
    housing = housing.cut(
        _cylinder_x(BEARING_POCKET_DIAMETER_MM, BEARING_POCKET_DEPTH_MM, 0)
    )
    housing = housing.cut(
        _cylinder_x(
            BEARING_POCKET_DIAMETER_MM,
            BEARING_POCKET_DEPTH_MM,
            HOUSING_LENGTH_MM - BEARING_POCKET_DEPTH_MM,
        )
    )
    housing = housing.cut(
        _cylinder_x(SHAFT_HOLE_DIAMETER_MM, HOUSING_LENGTH_MM + 2.0, -1.0)
    )

    # Hopper socket accepts the current 16 mm OD outlet.
    top_z = BARREL_OUTER_DIAMETER_MM / 2.0
    socket_start_z = top_z - 1.0
    socket_outer = (
        cq.Workplane("XY", origin=(INLET_CENTER_X_MM, 0, socket_start_z))
        .circle(HOPPER_SOCKET_OUTER_DIAMETER_MM / 2.0)
        .extrude(HOPPER_SOCKET_HEIGHT_MM + 1.0)
    )
    socket_inner = (
        cq.Workplane("XY", origin=(INLET_CENTER_X_MM, 0, socket_start_z - 0.5))
        .circle(HOPPER_SOCKET_INNER_DIAMETER_MM / 2.0)
        .extrude(HOPPER_SOCKET_HEIGHT_MM + 2.0)
    )
    housing = housing.union(socket_outer.cut(socket_inner))

    inlet_cut = (
        cq.Workplane("XY", origin=(INLET_CENTER_X_MM, 0, 0))
        .circle(INLET_CLEAR_DIAMETER_MM / 2.0)
        .extrude(BARREL_OUTER_DIAMETER_MM + 4.0, both=True)
    )
    housing = housing.cut(inlet_cut)

    # Downward discharge immediately before the outboard bearing.
    discharge_bottom_z = -BARREL_OUTER_DIAMETER_MM / 2.0 - DISCHARGE_LENGTH_MM
    discharge_outer = (
        cq.Workplane(
            "XY",
            origin=(DISCHARGE_CENTER_X_MM, 0, discharge_bottom_z),
        )
        .circle(DISCHARGE_OUTER_DIAMETER_MM / 2.0)
        .extrude(DISCHARGE_LENGTH_MM + 1.0)
    )
    discharge_inner = (
        cq.Workplane(
            "XY",
            origin=(DISCHARGE_CENTER_X_MM, 0, discharge_bottom_z - 0.5),
        )
        .circle(DISCHARGE_CLEAR_DIAMETER_MM / 2.0)
        .extrude(DISCHARGE_LENGTH_MM + 2.0)
    )
    housing = housing.union(discharge_outer.cut(discharge_inner))

    discharge_cut = (
        cq.Workplane(
            "XY",
            origin=(DISCHARGE_CENTER_X_MM, 0, discharge_bottom_z - 1.0),
        )
        .circle(DISCHARGE_CLEAR_DIAMETER_MM / 2.0)
        .extrude(BARREL_OUTER_DIAMETER_MM + DISCHARGE_LENGTH_MM + 4.0)
    )
    return housing.cut(discharge_cut).clean()


def build_assembly_compound() -> cq.Compound:
    return cq.Compound.makeCompound([build_housing().val(), build_screw().val()])


def _intersection_volume_mm3(a: cq.Workplane, b: cq.Workplane) -> float:
    intersection = a.intersect(b)
    return sum(float(solid.Volume()) for solid in intersection.solids().vals())


def inspect_model() -> dict:
    """Return deterministic geometry + sampled rotational-clearance evidence."""
    screw = build_screw()
    housing = build_housing()

    sample_angles = list(range(0, 360, ROTATION_SAMPLE_DEGREES))
    interference_volumes = [
        _intersection_volume_mm3(
            screw.rotate((0, 0, 0), (1, 0, 0), angle),
            housing,
        )
        for angle in sample_angles
    ]
    max_interference_mm3 = max(interference_volumes, default=0.0)

    annular_area_mm2 = math.pi / 4.0 * (
        FLIGHT_OUTER_DIAMETER_MM**2 - SHAFT_DIAMETER_MM**2
    )
    geometric_displacement_ml_per_rev = (
        annular_area_mm2 * FLIGHT_PITCH_MM / 1000.0
    )

    return {
        "screw_valid": bool(screw.val().isValid()),
        "screw_solid_count": len(screw.solids().vals()),
        "housing_valid": bool(housing.val().isValid()),
        "housing_solid_count": len(housing.solids().vals()),
        "shaft_diameter_mm": SHAFT_DIAMETER_MM,
        "flight_outer_diameter_mm": FLIGHT_OUTER_DIAMETER_MM,
        "flight_pitch_mm": FLIGHT_PITCH_MM,
        "flight_thickness_mm": FLIGHT_THICKNESS_MM,
        "barrel_inner_diameter_mm": BARREL_INNER_DIAMETER_MM,
        "radial_running_clearance_mm": round(
            (BARREL_INNER_DIAMETER_MM - FLIGHT_OUTER_DIAMETER_MM) / 2.0,
            6,
        ),
        "flight_turns": round(FLIGHT_LENGTH_MM / FLIGHT_PITCH_MM, 6),
        "housing_length_mm": HOUSING_LENGTH_MM,
        "hopper_socket_radial_clearance_mm": round(
            (
                HOPPER_SOCKET_INNER_DIAMETER_MM
                - HOPPER_OUTLET_OUTER_DIAMETER_MM
            )
            / 2.0,
            6,
        ),
        "inlet_clear_diameter_mm": INLET_CLEAR_DIAMETER_MM,
        "hopper_outlet_clear_diameter_mm": HOPPER_OUTLET_CLEAR_DIAMETER_MM,
        "discharge_clear_diameter_mm": DISCHARGE_CLEAR_DIAMETER_MM,
        "bearing_pocket_diameter_mm": BEARING_POCKET_DIAMETER_MM,
        "bearing_nominal_od_mm": BEARING_NOMINAL_OD_MM,
        "rotation_sample_count": len(sample_angles),
        "max_sampled_interference_mm3": round(max_interference_mm3, 9),
        "rotation_clearance_pass": max_interference_mm3 < 1e-6,
        "geometric_displacement_ml_per_rev": round(
            geometric_displacement_ml_per_rev,
            6,
        ),
    }



def viewer_spec() -> list[dict]:
    """Return browser-workbench entries for the auger assembly and subcomponents."""
    parameters = {
        "shaft_diameter_mm": SHAFT_DIAMETER_MM,
        "shaft_hole_diameter_mm": SHAFT_HOLE_DIAMETER_MM,
        "flight_outer_diameter_mm": FLIGHT_OUTER_DIAMETER_MM,
        "flight_pitch_mm": FLIGHT_PITCH_MM,
        "flight_thickness_mm": FLIGHT_THICKNESS_MM,
        "flight_start_x_mm": FLIGHT_START_X_MM,
        "flight_length_mm": FLIGHT_LENGTH_MM,
        "barrel_inner_diameter_mm": BARREL_INNER_DIAMETER_MM,
        "barrel_outer_diameter_mm": BARREL_OUTER_DIAMETER_MM,
        "housing_length_mm": HOUSING_LENGTH_MM,
        "inlet_center_x_mm": INLET_CENTER_X_MM,
        "inlet_clear_diameter_mm": INLET_CLEAR_DIAMETER_MM,
        "hopper_socket_inner_diameter_mm": HOPPER_SOCKET_INNER_DIAMETER_MM,
        "hopper_socket_outer_diameter_mm": HOPPER_SOCKET_OUTER_DIAMETER_MM,
        "hopper_socket_height_mm": HOPPER_SOCKET_HEIGHT_MM,
        "discharge_center_x_mm": DISCHARGE_CENTER_X_MM,
        "discharge_clear_diameter_mm": DISCHARGE_CLEAR_DIAMETER_MM,
        "discharge_outer_diameter_mm": DISCHARGE_OUTER_DIAMETER_MM,
        "discharge_length_mm": DISCHARGE_LENGTH_MM,
        "bearing_pocket_diameter_mm": BEARING_POCKET_DIAMETER_MM,
        "bearing_pocket_depth_mm": BEARING_POCKET_DEPTH_MM,
        "motor_side_shaft_extension_mm": MOTOR_SIDE_SHAFT_EXTENSION_MM,
        "outboard_shaft_extension_mm": OUTBOARD_SHAFT_EXTENSION_MM,
    }
    source = "https://github.com/bhadkamkar9snehil/HWThrowAway/blob/main/cad/auger.py"
    return [
        {
            "id": MODEL_ID,
            "name": "Auger meter V1",
            "type": "assembly",
            "view": "auger",
            "source": source,
            "simulation": "https://github.com/bhadkamkar9snehil/HWThrowAway/blob/main/simulation/auger/results/phase-01-rotation-clearance.json",
            "parameters": parameters,
        },
        {
            "id": "auger-screw-v1",
            "name": "Auger screw V1",
            "type": "subcomponent",
            "parent": MODEL_ID,
            "view": "screw",
            "source": source,
        },
        {
            "id": "auger-housing-v1",
            "name": "Auger housing V1",
            "type": "subcomponent",
            "parent": MODEL_ID,
            "view": "housing",
            "source": source,
        },
    ]


def export_all() -> None:
    root = Path(__file__).resolve().parents[1]
    exports = root / "exports"
    previews = root / "previews"
    exports.mkdir(parents=True, exist_ok=True)
    previews.mkdir(parents=True, exist_ok=True)

    screw = build_screw()
    housing = build_housing()
    assembly = build_assembly_compound()

    cq.exporters.export(screw, str(exports / "rangoli_auger_screw_v1.step"))
    cq.exporters.export(
        screw,
        str(exports / "rangoli_auger_screw_v1.stl"),
        tolerance=0.15,
        angularTolerance=0.15,
    )
    cq.exporters.export(housing, str(exports / "rangoli_auger_housing_v1.step"))
    cq.exporters.export(
        housing,
        str(exports / "rangoli_auger_housing_v1.stl"),
        tolerance=0.15,
        angularTolerance=0.15,
    )
    cq.exporters.export(
        assembly,
        str(exports / "rangoli_auger_assembly_v1.step"),
    )
    cq.exporters.export(
        assembly,
        str(exports / "rangoli_auger_assembly_v1.stl"),
        tolerance=0.15,
        angularTolerance=0.15,
    )
    cq.exporters.export(
        assembly,
        str(previews / "rangoli_auger_assembly_v1.svg"),
        opt={
            "width": 1100,
            "height": 700,
            "marginLeft": 40,
            "marginTop": 40,
            "showAxes": False,
            "projectionDir": (1.0, -1.0, 0.75),
        },
    )


if __name__ == "__main__":
    export_all()
