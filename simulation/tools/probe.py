# SPDX-FileCopyrightText: 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
# Upstream BSD-3-Clause notices and source map: root LICENSE and NOTICE.

"""Report the actuator v1 source geometry without changing it.

Run from the repository root with the workspace environment::

    PYTHONPATH="$PWD" python -m simulation.tools.probe
"""

from pathlib import Path

import cadquery as cq
import trimesh
from machinome.node.adapters.step import StepAssembly


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = PROJECT_ROOT / "mechanics" / "actuator_module_v1"


def rounded_bounds(bounds):
    return [[round(float(value), 4) for value in row] for row in bounds]


def report_stls():
    print("STL source inventory")
    for path in sorted((SOURCE_ROOT / "stl_files").glob("*.STL")):
        scene = trimesh.load(path, force="scene")
        bodies = list(scene.geometry.values())
        print(f"{path.name}: bodies={len(bodies)}")
        for index, mesh in enumerate(bodies):
            print(
                f"  [{index}] watertight={mesh.is_watertight} "
                f"bounds={rounded_bounds(mesh.bounds)} "
                f"centroid={[round(float(v), 4) for v in mesh.centroid]} "
                f"volume={float(mesh.volume):.4f}"
            )


def report_steps():
    print("STEP source inventory")
    for path in sorted((SOURCE_ROOT / "step_files").glob("*.STEP")):
        document = StepAssembly(path)
        shape = cq.importers.importStep(str(path)).val()
        bounds = shape.BoundingBox()
        xyz_bounds = [
            [bounds.xmin, bounds.ymin, bounds.zmin],
            [bounds.xmax, bounds.ymax, bounds.zmax],
        ]
        products = ", ".join(
            f"{product.name} ({product.kind}, {product.solid_count} solid)"
            for product in document.products
        )
        print(
            f"{path.name}: {products}; bounds={rounded_bounds(xyz_bounds)}; "
            f"volume={shape.Volume():.4f}"
        )


if __name__ == "__main__":
    report_stls()
    report_steps()
