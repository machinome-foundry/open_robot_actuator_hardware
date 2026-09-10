# SPDX-FileCopyrightText: 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
# Upstream BSD-3-Clause notices and source map: root LICENSE and NOTICE.

"""Brushless Actuator Module Core v1 simulation."""

import cadquery as cq
from molejo import P, Polygon, Shape, Teeth, Wrap

from solid_node.node import (
    AssemblyNode,
    CadQueryNode,
    MolejoNode,
    StepNode,
    StlNode,
)
from solid_node.motion.joints import Revolute
from solid_node.motion.ports import TranslationalPort
from solid_node.simulation import Driver, Instruction

from .layout import (
    AT3_PITCH,
    CENTER_CENTER,
    FIRST_BELT_TEETH,
    FIRST_BELT_WIDTH,
    FIRST_STAGE_Z,
    GEAR_PITCH_RADIUS,
    MOTOR_CENTER,
    OUTPUT_CENTER,
    PINION_PITCH_RADIUS,
    PITCH_ARC_PER_DEGREE,
    SECOND_BELT_TEETH,
    SECOND_BELT_WIDTH,
    SECOND_STAGE_Z,
    SEATING_GAP,
    STAGE_RATIO,
    TENSIONER_DEG_PER_MM,
    TENSIONER_X,
    TENSIONER_Y,
)


SOURCE_ROOT = "../mechanics/actuator_module_v1"


class MotorShaft(StepNode):
    """The upstream 3.99 mm by 33.4 mm custom motor shaft."""

    step_source = f"{SOURCE_ROOT}/step_files/motor_antigravity_4004_custom_shaft.STEP"
    color = "#aeb6bf"
    angular_deflection = 0.5


class MotorPulley(StepNode):
    """The upstream machined 10-tooth AT3 motor pulley."""

    step_source = f"{SOURCE_ROOT}/step_files/transmission_pulley_at3_t10_motor.STEP"
    color = "#d8dde3"
    angular_deflection = 0.5


class CodewheelMount(StlNode):
    """The upstream PWB codewheel mount used by actuator v1."""

    stl_source = f"{SOURCE_ROOT}/stl_files/encoder_codewheel_pwb_mount.STL"
    color = "#f2f2eb"


class CenterPinion(StepNode):
    """The upstream 19 mm center-shaft 10-tooth pulley."""

    step_source = f"{SOURCE_ROOT}/step_files/transmission_pulley_at3_t10_center.STEP"
    color = "#d8dde3"
    angular_deflection = 0.5

    spin = Revolute(axis=(0, 1, 0), unit="deg")


class CenterGear(StlNode):
    """The upstream printed 30-tooth first-stage pulley."""

    stl_source = f"{SOURCE_ROOT}/stl_files/transmission_pulley_at3_t30_center.STL"
    color = "#77cdd1"

    spin = Revolute(axis=(0, 0, 1), unit="deg")


class OutputPulley(StlNode):
    """The upstream printed 30-tooth output pulley."""

    stl_source = f"{SOURCE_ROOT}/stl_files/transmission_pulley_at3_t30_output.STL"
    color = "#77cdd1"

    spin = Revolute(axis=(0, 0, 1), unit="deg")


class TensionerRoller(StlNode):
    """The upstream default 10.0 mm tensioner roller."""

    stl_source = f"{SOURCE_ROOT}/stl_files/transmission_belt_tensioner_roller_10.0mm.STL"
    color = "#f2f2eb"

    spin = Revolute(axis=(0, 0, 1), unit="deg")


class MotorRotorEnvelope(CadQueryNode):
    """Non-production envelope for the documented 45 mm motor rotor."""

    color = "#30343b"

    def render(self):
        return (
            cq.Workplane("XY", origin=(0, 0, -14))
            .circle(22.5)
            .circle(20.0)
            .extrude(8.0)
        )


class MotorStatorEnvelope(CadQueryNode):
    """Reference stator ring; its unconstrained axial size is illustrative."""

    color = "#b87333"

    def render(self):
        return (
            cq.Workplane("XY", origin=(0, 0, -14))
            .circle(19.8)
            .circle(4.2)
            .extrude(8.0)
        )


class EncoderCodewheel(CadQueryNode):
    """Reference 25.56 mm OD / 7 mm ID optical codewheel."""

    color = "#262626"

    def render(self):
        return (
            cq.Workplane("XY", origin=(0, 0, -33.6))
            .circle(12.78)
            .circle(3.5)
            .extrude(0.2)
        )


class TransmissionBearing(CadQueryNode):
    """Reference 8 x 4 x 2 mm transmission bearing with running clearance."""

    color = "#c6ccd2"

    def render(self):
        return cq.Workplane("XY").circle(4.0).circle(2.02).extrude(2.0)


class OutputBearing(CadQueryNode):
    """Reference 32 x 25 x 4 mm output bearing with running clearance."""

    color = "#c6ccd2"

    def render(self):
        return cq.Workplane("XY").circle(16.0).circle(12.60).extrude(4.0)


class TensionerBearing(CadQueryNode):
    """Reference 7 x 3 x 3 mm tensioner bearing with running clearance."""

    color = "#c6ccd2"

    def render(self):
        return cq.Workplane("XY").circle(3.48).circle(1.55).extrude(3.0)


class MotorStack(AssemblyNode):
    """Rigidly driven motor rotor, shaft, pulley, and encoder stack."""

    turn = Revolute(axis=(0, 0, 1), unit="deg")

    rotor = MotorRotorEnvelope()
    shaft = MotorShaft()
    pulley = MotorPulley()
    codewheel_mount = CodewheelMount()
    codewheel = EncoderCodewheel()

    def render(self):
        # The pulley STEP is authored on +Y; +90 degrees places it on +Z.
        self.pulley.rotate(90, (1, 0, 0))
        # The assembly instructions put the mount about 2 mm from the shaft end.
        self.codewheel_mount.translate((0, 0, -28.7))


class CenterStack(AssemblyNode):
    """Coaxial 30-tooth gear and 10-tooth second-stage pinion."""

    pinion = CenterPinion()
    gear = CenterGear()
    lower_bearing = TransmissionBearing()
    upper_bearing = TransmissionBearing()

    def render(self):
        self.pinion.rotate(90, (1, 0, 0))
        self.lower_bearing.translate((0, 0, -2.0 - SEATING_GAP))
        self.upper_bearing.translate((0, 0, 19.0 + SEATING_GAP))


class OutputStack(AssemblyNode):
    """Driven output pulley and two shell-reference bearings."""

    pulley = OutputPulley()
    lower_bearing = OutputBearing()
    upper_bearing = OutputBearing()

    def render(self):
        self.pulley.translate((0, 0, SECOND_STAGE_Z))
        self.lower_bearing.translate((0, 0, SECOND_STAGE_Z - 8.2 - 4.0 - SEATING_GAP))
        self.upper_bearing.translate((0, 0, SECOND_STAGE_Z + 8.2 + SEATING_GAP))


class TensionerStack(AssemblyNode):
    """Default printed roller around its bought bearing."""

    roller = TensionerRoller()
    bearing = TensionerBearing()

    def render(self):
        self.roller.translate((0, 0, SECOND_STAGE_Z))
        self.bearing.translate((0, 0, SECOND_STAGE_Z - 1.0 + SEATING_GAP))


class FirstStageBelt(MolejoNode):
    """The documented 150 mm / 50-tooth / 4 mm AT3 belt."""

    color = "#d9b300"
    travel = TranslationalPort(unit="mm")

    def render(self):
        return Shape(
            profile=Polygon(
                [(-0.5, -FIRST_BELT_WIDTH / 2),
                 (0.5, -FIRST_BELT_WIDTH / 2),
                 (0.5, FIRST_BELT_WIDTH / 2),
                 (-0.5, FIRST_BELT_WIDTH / 2)]
            ),
            path=[Wrap(
                around=[
                    {"center": MOTOR_CENTER, "radius": PINION_PITCH_RADIUS},
                    {"center": CENTER_CENTER, "radius": GEAR_PITCH_RADIUS},
                ],
                teeth=Teeth(pitch=AT3_PITCH, height=0.8, count=FIRST_BELT_TEETH),
                phase=P.travel,
            )],
            path_samples=64,
            profile_samples=4,
            loop=True,
        )


class SecondStageBelt(MolejoNode):
    """The documented 201 mm / 67-tooth / 6 mm AT3 belt."""

    color = "#e6c229"
    travel = TranslationalPort(unit="mm")

    def render(self):
        return Shape(
            profile=Polygon(
                [(-0.5, -SECOND_BELT_WIDTH / 2),
                 (0.5, -SECOND_BELT_WIDTH / 2),
                 (0.5, SECOND_BELT_WIDTH / 2),
                 (-0.5, SECOND_BELT_WIDTH / 2)]
            ),
            path=[Wrap(
                around=[
                    {"center": CENTER_CENTER, "radius": PINION_PITCH_RADIUS},
                    {"center": OUTPUT_CENTER, "radius": GEAR_PITCH_RADIUS},
                ],
                teeth=Teeth(pitch=AT3_PITCH, height=0.8, count=SECOND_BELT_TEETH),
                phase=P.travel,
            )],
            path_samples=80,
            profile_samples=4,
            loop=True,
        )


class ActuatorModuleV1(AssemblyNode):
    """Visible root while the transmission is assembled ground-up."""

    input_angle = Driver(default=0.0, range=(0.0, 3240.0), unit="deg")

    instructions = {
        "Home": Instruction({"input_angle": 0.0}, duration=18.0),
        "Inspect Reduction": Instruction({"input_angle": 810.0}, duration=4.5),
        "One Output Turn": Instruction({"input_angle": 3240.0}, duration=18.0),
    }

    stator = MotorStatorEnvelope()
    motor_stack = MotorStack()
    center_stack = CenterStack()
    output_stack = OutputStack()
    upper_tensioner = TensionerStack()
    lower_tensioner = TensionerStack()
    first_belt = FirstStageBelt()
    second_belt = SecondStageBelt()

    input_angle.drives(motor_stack.turn)
    motor_stack.turn.drives(center_stack.gear.spin, ratio=STAGE_RATIO)
    center_stack.gear.spin.drives(center_stack.pinion.spin)
    center_stack.pinion.spin.drives(output_stack.pulley.spin, ratio=STAGE_RATIO)
    motor_stack.turn.drives(first_belt.travel, ratio=PITCH_ARC_PER_DEGREE)
    center_stack.pinion.spin.drives(second_belt.travel, ratio=PITCH_ARC_PER_DEGREE)
    second_belt.travel.drives(upper_tensioner.roller.spin, ratio=TENSIONER_DEG_PER_MM)
    second_belt.travel.drives(lower_tensioner.roller.spin, ratio=TENSIONER_DEG_PER_MM)

    def render(self):
        self.center_stack.translate((*CENTER_CENTER, 0))
        self.output_stack.translate((*OUTPUT_CENTER, 0))
        self.upper_tensioner.translate((TENSIONER_X, TENSIONER_Y, 0))
        self.lower_tensioner.translate((TENSIONER_X, -TENSIONER_Y, 0))
        self.first_belt.translate((0, 0, FIRST_STAGE_Z))
        self.second_belt.translate((0, 0, SECOND_STAGE_Z))
