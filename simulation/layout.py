# SPDX-FileCopyrightText: 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
# Upstream BSD-3-Clause notices and source map: root LICENSE and NOTICE.

"""Documented actuator v1 layout and derived pitch geometry."""

from math import asin, pi, sqrt


MOTOR_CENTER = (0.0, 0.0)
CENTER_CENTER = (43.9, 0.0)
OUTPUT_CENTER = (113.8, 0.0)

AT3_PITCH = 3.0
PINION_TEETH = 10
GEAR_TEETH = 30
FIRST_BELT_TEETH = 50
SECOND_BELT_TEETH = 67
FIRST_BELT_WIDTH = 4.0
SECOND_BELT_WIDTH = 6.0

PINION_PITCH_RADIUS = AT3_PITCH * PINION_TEETH / (2 * pi)
GEAR_PITCH_RADIUS = AT3_PITCH * GEAR_TEETH / (2 * pi)

STAGE_RATIO = PINION_TEETH / GEAR_TEETH
PITCH_ARC_PER_DEGREE = PINION_PITCH_RADIUS * pi / 180.0
TENSIONER_ROLLER_RADIUS = 5.0
TENSIONER_DEG_PER_MM = -180.0 / (TENSIONER_ROLLER_RADIUS * pi)

FIRST_STAGE_Z = 3.3
SECOND_STAGE_Z = 13.5
SEATING_GAP = 0.05

TENSIONER_X = CENTER_CENTER[0] + 6.2
TENSIONER_Y = 18.6


def open_belt_length(center_distance):
    """Pitch-line length for an open two-pulley belt."""

    radius_delta = GEAR_PITCH_RADIUS - PINION_PITCH_RADIUS
    tangent = sqrt(center_distance**2 - radius_delta**2)
    angle = asin(radius_delta / center_distance)
    return (
        2 * tangent
        + pi * (GEAR_PITCH_RADIUS + PINION_PITCH_RADIUS)
        + 2 * radius_delta * angle
    )


FIRST_PATH_LENGTH = open_belt_length(CENTER_CENTER[0] - MOTOR_CENTER[0])
SECOND_PATH_LENGTH = open_belt_length(OUTPUT_CENTER[0] - CENTER_CENTER[0])
