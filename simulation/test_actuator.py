# SPDX-FileCopyrightText: 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
# Upstream BSD-3-Clause notices and source map: root LICENSE and NOTICE.

"""Mechanical contracts for the Brushless Actuator Module Core v1."""

from math import hypot

import numpy as np

from machinome.simulation import ScenarioTest
from machinome.test import TestCase

from .actuator import ActuatorModuleV1
from .layout import FIRST_PATH_LENGTH, SECOND_PATH_LENGTH
from .seats import KNOWN_RIGID_OVERLAPS


def axis_xy(node):
    """Measure an axis center from the node's symmetric world-space bounds."""

    bounds = node.mesh.bounds
    return tuple((bounds[0][index] + bounds[1][index]) / 2 for index in (0, 1))


def rotate_vertices_about_z(vertices, center, angle_degrees):
    angle = np.deg2rad(angle_degrees)
    rotation = np.array(
        [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]
    )
    expected = vertices.copy()
    expected[:, :2] = (vertices[:, :2] - center) @ rotation.T + center
    return expected


def named_printed_solids(node, prefix=""):
    """Yield the framework's topmost rigid units with qualified tree names."""

    for child in node.children:
        path = f"{prefix}.{child.name}" if prefix else child.name
        if child.rigid:
            yield path, child
        else:
            yield from named_printed_solids(child, path)


class ActuatorContractMixin:
    def assert_expected_interference_inventory(self, root):
        solids = list(named_printed_solids(root))
        actual = set()
        for index, (left_name, left) in enumerate(solids):
            for right_name, right in solids[index + 1 :]:
                try:
                    self.assertNotIntersecting(left, right)
                except AssertionError:
                    actual.add(tuple(sorted((left_name, right_name))))
        self.assertEqual(actual, set(KNOWN_RIGID_OVERLAPS))


class ActuatorModuleV1Test(ActuatorContractMixin, TestCase):
    node = ActuatorModuleV1

    def assert_axis_xy(self, node, expected):
        measured = axis_xy(node)
        self.assertAlmostEqual(measured[0], expected[0], delta=0.02)
        self.assertAlmostEqual(measured[1], expected[1], delta=0.02)

    def test_motor_stack_axes_are_coaxial(self):
        motor = self.node.motor_stack
        for part in (motor.shaft, motor.pulley, motor.codewheel_mount):
            self.assert_axis_xy(part, (0.0, 0.0))

    def test_motor_shaft_uses_source_dimensions(self):
        shaft = self.node.motor_stack.shaft.mesh
        diameter = 2 * max(hypot(vertex[0], vertex[1]) for vertex in shaft.vertices)
        self.assertAlmostEqual(diameter, 3.99, delta=0.01)
        self.assertAlmostEqual(shaft.extents[2], 33.4, delta=0.01)

    def test_motor_source_solids_are_connected(self):
        self.assertNoDisconnectedSolids(self.node.motor_stack)

    def test_documented_shaft_stations(self):
        self.assert_axis_xy(self.node.motor_stack.shaft, (0.0, 0.0))
        self.assert_axis_xy(self.node.center_stack.gear, (43.9, 0.0))
        self.assert_axis_xy(self.node.output_stack.pulley, (113.8, 0.0))

    def test_center_stack_is_coaxial(self):
        center = self.node.center_stack
        for part in (center.pinion, center.gear):
            self.assert_axis_xy(part, (43.9, 0.0))

    def test_output_bearings_are_coaxial(self):
        output = self.node.output_stack
        for part in (output.pulley, output.lower_bearing, output.upper_bearing):
            self.assert_axis_xy(part, (113.8, 0.0))

    def test_belts_use_documented_sizes(self):
        belts = (
            (self.node.first_belt, 50, 4.0),
            (self.node.second_belt, 67, 6.0),
        )
        for belt, tooth_count, width in belts:
            document = belt.render().to_dict()
            wrap = document["path"][0]
            self.assertEqual(wrap["teeth"]["pitch"], 3.0)
            self.assertEqual(wrap["teeth"]["count"], tooth_count)
            self.assertAlmostEqual(belt.mesh.extents[2], width, delta=0.02)

    def test_documented_centers_close_nominal_belts(self):
        self.assertAlmostEqual(FIRST_PATH_LENGTH, 149.8855, delta=0.0001)
        self.assertAlmostEqual(SECOND_PATH_LENGTH, 201.1066, delta=0.0001)
        self.assertLess(abs(FIRST_PATH_LENGTH - 150.0), 0.12)
        self.assertLess(abs(SECOND_PATH_LENGTH - 201.0), 0.12)

    def test_belts_circulate_with_input(self):
        self.node.set_state(input_angle=0.0)
        first_home = self.node.first_belt.mesh.vertices.copy()
        second_home = self.node.second_belt.mesh.vertices.copy()
        # 90 degrees advances the first stage by 2.5 teeth; 180 would be a
        # five-tooth periodic phase and would intentionally look unchanged.
        self.node.set_state(input_angle=90.0)
        first_moved = self.node.first_belt.mesh.vertices
        second_moved = self.node.second_belt.mesh.vertices
        self.assertGreater(np.max(np.abs(first_moved - first_home)), 0.1)
        self.assertGreater(np.max(np.abs(second_moved - second_home)), 0.1)
        self.node.set_state(input_angle=0.0)

    def test_rigid_stacks_follow_two_stage_reduction(self):
        self.node.set_state(input_angle=0.0)
        motor_home = self.node.motor_stack.pulley.mesh.vertices.copy()
        center_home = self.node.center_stack.gear.mesh.vertices.copy()
        output_home = self.node.output_stack.pulley.mesh.vertices.copy()

        self.node.set_state(input_angle=810.0)
        expectations = (
            (self.node.motor_stack.pulley.mesh.vertices, motor_home, (0.0, 0.0), 810.0),
            (self.node.center_stack.gear.mesh.vertices, center_home, (43.9, 0.0), 270.0),
            (self.node.output_stack.pulley.mesh.vertices, output_home, (113.8, 0.0), 90.0),
        )
        for moved, home, center, angle in expectations:
            expected = rotate_vertices_about_z(home, np.array(center), angle)
            np.testing.assert_allclose(moved, expected, atol=0.02)
        self.node.set_state(input_angle=0.0)

    def test_solid_integrity(self):
        self.assertNoDisconnectedSolids(self.node)

    def test_assembly_integrity(self):
        self.assert_expected_interference_inventory(self.node)

    def test_known_center_press_fit_volume(self):
        seat = KNOWN_RIGID_OVERLAPS[("center_stack.gear", "center_stack.pinion")]
        self.assertIntersectVolumeAbove(
            self.node.center_stack.pinion,
            self.node.center_stack.gear,
            seat["minimum_volume_mm3"],
        )
        self.assertIntersectVolumeBelow(
            self.node.center_stack.pinion,
            self.node.center_stack.gear,
            seat["maximum_volume_mm3"],
        )


class ActuatorModuleV1ScenarioTest(ActuatorContractMixin, ScenarioTest):
    node = ActuatorModuleV1
    dt = 0.5
    meshes = True

    def test_instructions_land_exactly(self):
        sim = self.simulation()
        sim.every(1.5, self.assert_expected_interference_inventory, self.node)
        sim.at(0.0).trigger("Inspect Reduction")
        sim.run(4.5)
        self.assertEqual(sim.state["input_angle"], 810.0)

        sim.at(sim.time).trigger("One Output Turn")
        sim.run(18.0)
        self.assertEqual(sim.state["input_angle"], 3240.0)

        sim.at(sim.time).trigger("Home")
        sim.run(18.0)
        self.assertEqual(sim.state["input_angle"], 0.0)
