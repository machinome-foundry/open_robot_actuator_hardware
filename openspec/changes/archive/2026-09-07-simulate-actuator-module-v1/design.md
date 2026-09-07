## Context

The repository is BSD-3-Clause hardware documentation containing several robots and test fixtures. Its reusable Brushless Actuator Module Core v1 is documented as a 160 mm segment with a 43.9 mm motor-to-center distance, a 69.9 mm center-to-output distance, and two 10:30 AT3 belt stages. It ships three single-product STEP files (the 33.4 mm custom motor shaft and both 10-tooth pulleys), watertight single-body STLs for both 30-tooth pulleys, the encoder mounts, and six tensioner roller sizes. Bought components and the robot-specific shell that seats the mechanism are not supplied as core CAD.

The source meshes do not share an assembly frame: the STL pulley axes are +Z, the two STEP pulley axes are +Y with an end face at Y=0, and the motor shaft STEP is on Z from -33.4 mm to 0. The source drawings and assembly photos establish how these frames meet. A retained `simulation/tools/probe.py` will reproduce the body count, watertightness, bounds, centroids, and STEP product inventory used here.

### Coordinates

- The machine frame is right-handed millimetres with the motor axis at `(0, 0)`, the center axis at `(43.9, 0)`, and the output axis at `(113.8, 0)` in XY. +Z follows the shipped STL print direction and is the common shaft axis.
- `input_angle` is the motor rotor and shaft angle in degrees about +Z. Positive input produces positive center angle `input_angle / 3` and positive output angle `input_angle / 9`; both belt stages are open, not crossed.
- The first-stage 4 mm belt occupies the source motor-pulley and center-gear plane. The second-stage 6 mm belt occupies the exposed end of the 19 mm center pinion and the shifted output gear plane.
- A named 0.05 mm visual seating gap distinguishes adjacent bought hardware surfaces that otherwise coincide.

## Goals / Non-Goals

**Goals:**

- Preserve every shipped CAD file byte-for-byte and import the production parts from their own sources.
- Make the actuator's only external mechanical meaning—input shaft angle—directly controllable while all internal rotations and belt travel follow.
- Make the two reduction stages, belt planes, shaft centers, bearings, and encoder-side parts visible and contract-tested.
- Leave a finite build, inspectable snapshots, a small instruction demo, measurements, and project-owned specifications.

**Non-Goals:**

- Simulate the repository's robot-specific shells, legs, bodies, electronics, or control firmware.
- Predict torque, compliance, tooth load, backlash under load, belt tension, motor electromagnetics, thermal behaviour, fastener preload, or service life.
- Certify upstream meshes as manufacturable or repair source tolerances.

## Decisions

### Import production geometry and draw only missing catalogue hardware

`StepNode` imports the three STEP products, rotating the pulley files from +Y to +Z. `StlNode` imports the v1 30-tooth center/output pulleys, PWB codewheel mount, and default 10.0 mm tensioner rollers. CadQuery leaves provide simple material-coloured envelopes for the documented 45 mm motor rotor/stator, 8x4x2 mm and 32x25x4 mm bearings, and the 25.56 mm codewheel. These envelopes are explicitly non-production geometry; copying or replacing supplied CAD was rejected because it would make the simulation a fork of the design.

### Treat each rigidly driven stack as a port-owned subassembly

Motor, center, output, and tensioner stacks each declare an angle port and apply that angle in their own `simulate()`. The root binds every port from `input_angle`; belt nodes own travel ports. This keeps the machine's one control separate from the internal joints and lets later robot-specific changes expose a joint without restructuring the core.

### Use pitch-circle kinematics from the documented AT3 tooth counts

Pitch radii are `3 mm * teeth / (2*pi)`. At the documented shaft centers, the ideal two-pulley path lengths are 149.886 mm and 201.107 mm, within 0.115 mm of the nominal 150 mm and 201 mm belt lengths before tensioner deflection. Molejo `Wrap` shapes therefore use the pitch circles and the real 50/67 tooth counts. The tensioner rollers are shown at the documented second-stage location but the flexible path remains the analytically closed two-pulley datum; modelling preload without a specified installed deflection was rejected as false precision.

### Use three slow inspection instructions

`Home` returns input to 0 degrees, `Inspect Reduction` advances input 810 degrees so the center turns 270 degrees and output 90 degrees, and `One Output Turn` advances input 3240 degrees so the output turns once. The demo rate is 180 input degrees per second: intentionally slow enough to inspect, and not a claim about the motor's electrical speed limit.

### Keep unsupported structure out of the model

The actuator core is held by a robot-specific shell, but no single shell belongs to the reusable core. The model includes reference bearings and motor stator to make seats and axes legible, but does not invent a frame or claim a freestanding support contract. Robot shells remain later named models.

## Findings

- The published center distances and pitch radii almost exactly close the nominal belts: 149.886 mm versus 150 mm and 201.107 mm versus 201 mm. This supports the drawing's geometry independently of the assembly image.
- The file named `motor_antigravity_4004_custom_shaft.STEP` contains one 3.99 mm-diameter, 33.4 mm-long shaft solid rather than the whole motor; the motor body must therefore remain catalogue/reference geometry.
- The center 10-tooth STEP is 19 mm long while its toothed portion runs from 2.5 mm to 16.5 mm. It both keys into the printed 30-tooth center pulley and leaves a second belt track exposed, explaining the compact coaxial two-stage stack.
- At the documented shared origin, the upstream center-pinion STEP and center-gear STL overlap by 0.104727 mm³ on the faceted geometry. The assembly instructions define this as a press-fit subassembly; `simulation/seats.py` records the pair and bounded volume so a new, changed, or removed overlap fails instead of being hidden by an epsilon.
- The core cannot prove shell bearing-seat support or whole-actuator non-interference without choosing one of the repository's robot-specific shell designs. This first model proves the reusable transmission only.

### Findings for the framework

None at proposal time.

## Risks / Trade-offs

- [Reference hardware can look more exact than it is] -> Give it distinct colours, name it as an envelope in the tree and README, and exclude its unconstrained axial thicknesses from dimensional contracts.
- [A belt path without specified tensioner preload omits local deflection] -> Preserve the exact nominal belt length comparison and place the rollers as reference hardware; record this as a model limit instead of guessing preload.
- [Imported faceted pulley geometry can make exact fusion slow] -> Keep manufactured pieces as separate rigid nodes and use the faceted kernel during development, with one exact certification run at the end.
- [The repository covers several machines] -> Declare only `actuator-module-v1` now and leave the manifest ready for additional named models rather than implying the robots are simulated.
