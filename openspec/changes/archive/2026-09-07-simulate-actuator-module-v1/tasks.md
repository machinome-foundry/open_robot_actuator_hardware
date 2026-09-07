## 1. Project record and visible root

- [x] 1.1 Add the root manifest, simulation package, ignored build outputs, and a minimal `ActuatorModuleV1` root that builds visibly.
- [x] 1.2 Add `simulation/tools/probe.py` and record the reproducible STEP/STL inventory and coordinate readings in `docs/measurements.md`.

## 2. Motor stack

- [x] 2.1 Add red contracts for the motor shaft/pulley coaxiality, source geometry, and one-body integrity.
- [x] 2.2 Import the shaft, motor pulley, and PWB codewheel mount; add the documented motor and codewheel reference hardware; make the motor stack contracts green.
- [x] 2.3 Mutation-check that shifting the motor pulley axis is caught by the coaxiality contract, then restore green.

## 3. Center and output stacks

- [x] 3.1 Add red contracts for the 43.9 mm and 69.9 mm shaft spacing, the center-pulley coaxial stack, and output-bearing coaxiality.
- [x] 3.2 Import the center pinion, center gear, output gear, and default tensioner rollers; add catalogue bearing geometry and make the stack contracts green.
- [x] 3.3 Mutation-check that a wrong center station and a tilted output bearing are caught by their specific contracts, then restore green.

## 4. Belt stages

- [x] 4.1 Add red contracts for the AT3 pitch, tooth counts, widths, nominal closed path lengths, and belt response to input motion.
- [x] 4.2 Add the two molejo belt wraps and tensioner reference placements, bind their travel ports, and make the belt contracts green.
- [x] 4.3 Mutation-check that an incorrect second-stage tooth count is caught by the belt contract, then restore green.

## 5. Root controls and demonstration

- [x] 5.1 Add red motion contracts for the 3:1 and 9:1 geometry transforms and scenario endpoints.
- [x] 5.2 Bind every stack port to the `input_angle` driver, add `Home`, `Inspect Reduction`, and `One Output Turn`, and make the motion contracts green.
- [x] 5.3 Add swept rigid-body non-interference and connectivity contracts and a scenario that triggers every instruction.
- [x] 5.4 Mutation-check that a wrong output ratio is caught by the output geometry transform contract, then restore green.

## 6. Evidence, instructions, and closeout

- [x] 6.1 Run the faceted regression for every node file, build the manifest root, and inspect `viewer.json` for the root, parts, driver, bindings, and instructions.
- [x] 6.2 Render and visually inspect an isometric home snapshot, an axis-alignment view, and an inspection-pose snapshot; keep generated images out of Git.
- [x] 6.3 Document the exact commands, controls, instructions, ground-up model sequence, findings, and limits in the project README.
- [x] 6.4 Run the exact regression for every node file, validate the OpenSpec change, sync the accepted specifications, and archive the completed change.
