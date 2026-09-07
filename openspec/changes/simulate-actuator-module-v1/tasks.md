## 1. Project record and visible root

- [ ] 1.1 Add the root manifest, simulation package, ignored build outputs, and a minimal `ActuatorModuleV1` root that builds visibly.
- [ ] 1.2 Add `simulation/tools/probe.py` and record the reproducible STEP/STL inventory and coordinate readings in `docs/measurements.md`.

## 2. Motor stack

- [ ] 2.1 Add red contracts for the motor shaft/pulley coaxiality, source geometry, and one-body integrity.
- [ ] 2.2 Import the shaft, motor pulley, and PWB codewheel mount; add the documented motor and codewheel reference hardware; make the motor stack contracts green.
- [ ] 2.3 Mutation-check that shifting the motor pulley axis is caught by the coaxiality contract, then restore green.

## 3. Center and output stacks

- [ ] 3.1 Add red contracts for the 43.9 mm and 69.9 mm shaft spacing, the center-pulley coaxial stack, and output-bearing coaxiality.
- [ ] 3.2 Import the center pinion, center gear, output gear, and default tensioner rollers; add catalogue bearing geometry and make the stack contracts green.
- [ ] 3.3 Mutation-check that a wrong center station and a tilted output bearing are caught by their specific contracts, then restore green.

## 4. Belt stages

- [ ] 4.1 Add red contracts for the AT3 pitch, tooth counts, widths, nominal closed path lengths, and belt response to input motion.
- [ ] 4.2 Add the two molejo belt wraps and tensioner reference placements, bind their travel ports, and make the belt contracts green.
- [ ] 4.3 Mutation-check that an incorrect second-stage tooth count is caught by the belt contract, then restore green.

## 5. Root controls and demonstration

- [ ] 5.1 Add red motion contracts for the 3:1 and 9:1 geometry transforms and scenario endpoints.
- [ ] 5.2 Bind every stack port to the `input_angle` driver, add `Home`, `Inspect Reduction`, and `One Output Turn`, and make the motion contracts green.
- [ ] 5.3 Add swept rigid-body non-interference and connectivity contracts and a scenario that triggers every instruction.
- [ ] 5.4 Mutation-check that a wrong output ratio is caught by the output geometry transform contract, then restore green.

## 6. Evidence, instructions, and closeout

- [ ] 6.1 Run the faceted regression for every node file, build the manifest root, and inspect `viewer.json` for the root, parts, driver, bindings, and instructions.
- [ ] 6.2 Render and visually inspect an isometric home snapshot, an axis-alignment view, and an inspection-pose snapshot; keep generated images out of Git.
- [ ] 6.3 Document the exact commands, controls, instructions, ground-up model sequence, findings, and limits in the project README.
- [ ] 6.4 Run the exact regression for every node file, validate the OpenSpec change, sync the accepted specifications, and archive the completed change.
