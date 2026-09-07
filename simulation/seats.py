# SPDX-FileCopyrightText: 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
# Upstream BSD-3-Clause notices and source map: root LICENSE and NOTICE.

"""Measured upstream rigid-body overlaps admitted as an exact inventory.

These are source-geometry findings, not tolerances. A changed, removed, or new
overlap must fail the contracts and be investigated.
"""


KNOWN_RIGID_OVERLAPS = {
    ("center_stack.gear", "center_stack.pinion"): {
        "measured_volume_mm3": 0.10472716970402911,
        "minimum_volume_mm3": 0.08,
        "maximum_volume_mm3": 0.13,
        "reason": "Upstream press-fit center pulley sources at their shared origin",
    },
}
