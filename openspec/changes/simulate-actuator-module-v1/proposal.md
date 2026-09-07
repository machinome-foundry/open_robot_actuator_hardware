## Why

The actuator repository publishes the individual pulleys, shaft, assembly instructions, and dimensional evidence, but it does not provide an executable machine that proves the two belt stages stay aligned and transmit the documented 9:1 reduction. The requested scope is verbatim: **"use simulate-project skill and simulate Actuators/open_robot_actuator_hardware"**; because the repository contains several downstream robots, this change takes its namesake reusable Brushless Actuator Module Core v1 as the first simulated machine.

## What Changes

- Add a thin `simulation/` layer that imports the actuator's shipped STEP and STL parts without editing or redrawing them, and represents the documented bought motor, bearings, codewheel, and belt tensioners from catalogue dimensions.
- Assemble the v1 motor, center, and output axes at the documented 43.9 mm and 69.9 mm center distances, with each part carrying a material-identifying colour.
- Add one builder-facing `input_angle` driver in degrees. The center shaft follows at 1/3 input speed and the output follows at 1/9 input speed through the two documented 10:30 AT3 stages.
- Add `Home`, `One Output Turn`, and `Inspect Reduction` instructions with physically meaningful durations and exact landing targets.
- Represent the 150 mm and 201 mm toothed belts as moving flexible parts and prove the shaft spacing, pulley coaxiality, bearing seats, reduction, instruction endpoints, connectivity, and rigid-part non-interference with contracts and mutation checks.
- Add build, test, snapshot, and control instructions to the upstream README, including measured findings and explicit simulation limits.

## Capabilities

### New Capabilities

- `actuator-core-assembly`: The v1 core's imported and catalogue components occupy the documented shaft layout and preserve their physical interfaces.
- `dual-stage-belt-drive`: A single actuator input moves both timing-belt stages and the output at the documented reduction, with inspectable poses and scenario contracts.

### Modified Capabilities

None.

## Impact

- Adds a root `pyproject.toml` manifest, the `simulation/` Python package and tests, and project-owned OpenSpec records.
- Adds solid-node and molejo as development/runtime requirements for the simulation only; no existing electronics, mechanics, STEP, STL, image, drawing, or instruction file is edited.
- Uses `mechanics/actuator_module_v1/` as the source of truth. The repository's other robot, leg, finger, and testbed assemblies are out of scope because each adds its own shell geometry and kinematic meanings; they can become separate named models later.
- The core simulation verifies geometry and kinematics, not torque, belt tension, tooth elasticity, encoder electronics, fastener preload, or manufacturing fitness.
