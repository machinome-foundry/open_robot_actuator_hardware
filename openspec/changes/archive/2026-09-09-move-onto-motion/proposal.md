# Move the actuator module v1 simulation onto solid-node's motion layer

## Why

solid-node main integrated `solid_node.motion` (ADR-087..089): ports and
`Time` left `solid_node.node` with NO re-export. `simulation/actuator.py`
therefore no longer imports on the current framework — confirmed here with
one import, before any edit:

    ImportError: module 'solid_node.node' has no attribute 'RotationalPort':
    ports and the declared time base moved to 'solid_node.motion.ports'.

(The campaign tracker's note "imports not broken" for this project is
wrong; see **Pre-existing state**.) It is the only module that imports a
moved name — `simulation/test_actuator.py`, `simulation/seats.py`,
`simulation/layout.py` and `simulation/tools/probe.py` all import fine.

Fixing that import alone would leave the machine stated the old way: four
`RotationalPort`s whose only job is to carry one angle down one level,
four `simulate()` bodies that fan that angle out with hand-written
`rotate()` calls, one of them with the frame inversion written out by hand
(`self.pulley.rotate(angle, (0, 1, 0))`, correct only because that STEP is
authored on +Y and its rest placement turns it onto +Z), and a two-stage
belt reduction that exists only as three divisions in the root's
`simulate()` — `input/3`, `input/9` — rather than as the two 10-into-30
meshes it actually is.

The motion layer says what a body is FREE to do, once, next to the body,
and what drives what, as a sentence. This machine fits it exactly: every
freedom is a turn about a line parallel to +Z that the sources already
fix, and the whole actuator is one train from the motor can to the output
flange, with the two belts riding it. Stated that way the project loses
all four ports, all four fan-out `simulate()` bodies AND the root's, and
gains 5 joint declarations (6 freedoms) and 8 relations that read as the
mechanism. Nothing about the geometry, the placements, the control
surface or any pose changes.

**No missing primitive; no deferral.** This actuator has no planetary
stage at all — it is a dual-stage AT3 belt drive (10T → 30T twice, 9:1),
so there are no planets, nested or sibling, and no orbit. No body carries
two joints, so the composition-order gap is not touched. Nothing in the
tree is `.repeat()`ed or list-held, so the fan-out gap is not touched. No
relation needs two sources, and no ratio adds a bare number to a
dimensioned token (no `Length`/`Count` parameter is declared anywhere in
this simulation; every layout number is a plain float in
`simulation/layout.py`).

## What changes

Only `simulation/actuator.py`, plus four named constants added to
`simulation/layout.py` beside the numbers they come from.

### The five joint declarations (six freedoms)

`axis` and `at` are stated in the PARENT's frame, as the framework
requires. Every axis is `(0, 0, 1)`: `test_documented_shaft_stations`,
`test_center_stack_is_coaxial` and `test_output_bearings_are_coaxial`
already assert that each station is on its own +Z line, and
`openspec/specs/actuator-core-assembly/spec.md` requires the three axes
parallel to +Z. No joint declares a `range`: the actuator turns without
limit and the builder-facing limit stays on the `input_angle` driver
(0..3240°, nine motor turns).

| # | Class | Joint | `axis` | `at`, in the parent's frame | Where the numbers come from |
|---|---|---|---|---|---|
| 1 | `MotorStack` (assembly) | `turn` | `(0, 0, 1)` | `(0, 0, 0)` — the default, the motor axis | `ActuatorModuleV1.render()` does not place `motor_stack` at all, so its rest placement is the identity and the machine axis IS its placed origin. Replaces the whole of `MotorStack.simulate()`: five `rotate` calls, one of them the hand-inverted `(0, 1, 0)` one |
| 2 | `CenterGear` (leaf) | `spin` | `(0, 0, 1)` | `(0, 0, 0)` — the default, the centre axis in `CenterStack`'s frame | `CenterStack.render()` leaves the gear at the stack origin; replaces `self.gear.rotate(angle, AXIS)` |
| 3 | `CenterPinion` (leaf) | `spin` | `(0, 0, 1)` | `(0, 0, 0)` — the default | the pinion is placed by `rotate(90, (1, 0, 0))` only, so the stack's z line still passes through its placed origin; the framework carries the axis into the part's own frame as `(0, 1, 0)`, which is exactly the hand-written `self.pinion.rotate(angle, (0, 1, 0))` the comment there explains |
| 4 | `OutputPulley` (leaf) | `spin` | `(0, 0, 1)` | `(0, 0, SECOND_STAGE_Z)` = `(0, 0, 13.5)` in `OutputStack`'s frame | exactly `OutputStack.render()`'s `translate((0, 0, SECOND_STAGE_Z))`, i.e. the pulley's own placed origin, written so the local anchor is zero and the joint emits ONE rotation with no centring translations. Replaces `self.pulley.rotate(angle, AXIS)` |
| 5 | `TensionerRoller` (leaf, TWO instances) | `spin` | `(0, 0, 1)` | `(0, 0, SECOND_STAGE_Z)` in `TensionerStack`'s frame | exactly `TensionerStack.render()`'s `translate((0, 0, SECOND_STAGE_Z))`. One class serves both tensioners because both rollers sit identically INSIDE their stack; the two stacks differ only in the root's `translate`, which the joint never sees. Replaces `self.roller.rotate(angle, AXIS)` |

Joint 1 is on the assembly because the motor stack is one rigid body: the
rotor, the shaft, the pulley, the codewheel mount and the codewheel all
turn together and nothing in it stands still. Joints 2–5 are on the leaves
because their stacks are NOT one body: `CenterStack`, `OutputStack` and
`TensionerStack` each also hold bearings that the model deliberately keeps
still. Putting one joint on those assemblies would turn their bearings
too, which is a different pose (a rotationally symmetric mesh still has a
different world matrix) — see **What does not change**.

`CenterGear` and `CenterPinion` are a press fit, so they are one body in
the hardware; they stay two nodes with two joints and a unit relation
between them because `seats.py` records that press fit as an exact
interference pair `("center_stack.gear", "center_stack.pinion")` and
`test_known_center_press_fit_volume` measures it. Nothing in the tree is
renamed.

### The four constants added to `simulation/layout.py`

All four are numbers `actuator.py` writes inline today, moved next to the
geometry they come from so each is written once and the relations read it:

```python
STAGE_RATIO = PINION_TEETH / GEAR_TEETH          # 10/30, one belt stage
PITCH_ARC_PER_DEGREE = PINION_PITCH_RADIUS * pi / 180.0   # mm of belt per degree of a 10T pulley
TENSIONER_ROLLER_RADIUS = 5.0                    # the 10.0 mm roller STL
TENSIONER_DEG_PER_MM = -180.0 / (TENSIONER_ROLLER_RADIUS * pi)
```

`STAGE_RATIO` and `PITCH_ARC_PER_DEGREE` replace the literal `3.0`, `9.0`
and `PINION_PITCH_RADIUS * pi / 180.0` in the root's `simulate()`;
`TENSIONER_ROLLER_RADIUS` names the `5.0` that is hard-coded in
`ActuatorModuleV1.simulate()` today and comes from the roller's own source
file name, `transmission_belt_tensioner_roller_10.0mm.STL`.

**On exactness.** Today the root computes `input/3.0` and `input/9.0` by
division; the relations multiply by `STAGE_RATIO` and chain two stages, so
individual values differ in the last ulp (≈1e-13° at the largest pose,
3240°). `capture_poses.py` rounds every matrix entry and port value to 9
decimals and compares at `--tol 1e-9`, so the pose comparison is expected
to read max deviation 0 all the same; the largest test tolerance in play
is `atol=0.02` on vertices. If the implementer sees a non-zero deviation,
it is a real regression, not this — stop and report.

### The eight `drives` sentences

All eight are stated in `ActuatorModuleV1`'s class body — one class body,
as the framework's chain rule requires (see **Known gaps**) — and every
end names its coordinate.

| # | Sentence | Both ends named | Law | Source of the numbers |
|---|---|---|---|---|
| 1 | `input_angle.drives(motor_stack.turn)` | root `Driver input_angle` → `MotorStack.turn` | ratio 1 (default `Affine`) | the rotor IS the input; replaces `self.motor_stack.angle = self.input_angle` |
| 2 | `motor_stack.turn.drives(center_stack.gear.spin, ratio=STAGE_RATIO)` | `MotorStack.turn` → `CenterGear.spin` | `ratio = 10/30` | first belt stage: the 10-tooth motor pulley `transmission_pulley_at3_t10_motor.STEP` into the 30-tooth `transmission_pulley_at3_t30_center.STL`; `PINION_TEETH`/`GEAR_TEETH` in `layout.py`. Today's `input_angle / 3.0`, asserted by `test_rigid_stacks_follow_two_stage_reduction` (810° in → 270° at the centre) |
| 3 | `center_stack.gear.spin.drives(center_stack.pinion.spin)` | `CenterGear.spin` → `CenterPinion.spin` | ratio 1 | the press fit `seats.py` records: the printed 30T pulley and the machined 10T centre pulley are one turned body. Today both take the same `angle` |
| 4 | `center_stack.pinion.spin.drives(output_stack.pulley.spin, ratio=STAGE_RATIO)` | `CenterPinion.spin` → `OutputPulley.spin` | `ratio = 10/30` | second belt stage: the 10-tooth `transmission_pulley_at3_t10_center.STEP` into the 30-tooth `transmission_pulley_at3_t30_output.STL`. Composed with #2 this is the documented 9:1, today's `input_angle / 9.0`, asserted by the same test (810° in → 90° at the output) |
| 5 | `motor_stack.turn.drives(first_belt.travel, ratio=PITCH_ARC_PER_DEGREE)` | `MotorStack.turn` → `FirstStageBelt.travel` (`TranslationalPort`) | `ratio = PINION_PITCH_RADIUS·π/180` mm per degree | the belt is pulled by the 10T motor pulley at its pitch radius, `AT3_PITCH * PINION_TEETH / 2π` (`layout.py`); today's `self.first_belt.travel = self.input_angle * PINION_PITCH_RADIUS * pi / 180.0` |
| 6 | `center_stack.pinion.spin.drives(second_belt.travel, ratio=PITCH_ARC_PER_DEGREE)` | `CenterPinion.spin` → `SecondStageBelt.travel` | same ratio | the second belt is pulled by the centre 10T pulley, the same pitch radius; today's `second_belt_travel = center_angle * PINION_PITCH_RADIUS * pi / 180.0` |
| 7 | `second_belt.travel.drives(upper_tensioner.roller.spin, ratio=TENSIONER_DEG_PER_MM)` | `SecondStageBelt.travel` → `TensionerRoller.spin` (upper) | `ratio = -180/(5·π)` deg per mm | the roller is turned BY the belt it rides, backwards, at its own 5 mm radius; today's `-second_belt_travel * 180.0 / (5.0 * pi)` |
| 8 | `second_belt.travel.drives(lower_tensioner.roller.spin, ratio=TENSIONER_DEG_PER_MM)` | `SecondStageBelt.travel` → `TensionerRoller.spin` (lower) | same | the lower tensioner takes the same value today, and the two rollers ride the same belt |

`second_belt.travel` is the DRIVEN end of #6 and the SOURCE of #7 and #8:
one binder, several readers, which is what the couplings spec allows.

Rejected alternative for #7 and #8: drive the rollers straight from
`center_stack.pinion.spin` with the composed ratio
`-PINION_PITCH_RADIUS / TENSIONER_ROLLER_RADIUS`. It is one number instead
of two, but it says the pinion turns the roller, and it does not — the
belt does. The chain as written is both the mechanism and today's exact
arithmetic.

### Derived coordinates

**None.** Every relation here is one coordinate into one coordinate
through a constant; no formula over two coordinates is needed anywhere in
this machine.

### The four ports that disappear, and the two that stay

Gone — each carried one angle down exactly one level and fanned it out:

| Port | Today | After |
|---|---|---|
| `MotorStack.angle` (`RotationalPort`) | the root binds it; `simulate()` fans it into five `rotate` calls | joint 1 |
| `CenterStack.angle` | the root binds it; `simulate()` fans it into two `rotate` calls | joints 2 and 3, relations 2 and 3 |
| `OutputStack.angle` | the root binds it; `simulate()` turns the pulley | joint 4, relation 4 |
| `TensionerStack.angle` (both instances) | the root binds it; `simulate()` turns the roller | joint 5, relations 7 and 8 |

Staying, because they are geometry inputs and not forwarders — the same
case as fender-bender's `drop`:

- `FirstStageBelt.travel` and `SecondStageBelt.travel`
  (`TranslationalPort`). Each is read INSIDE the belt's own `render()` as
  molejo's `phase=P.travel` on a `Wrap`, so the value shapes the belt
  rather than being handed on to a child. The chain is
  driver → relation → port → geometry, exactly as `docs/driving.rst`
  describes it for a flexible part. They keep their names, so
  `test_belts_circulate_with_input` and `test_belts_use_documented_sizes`
  are untouched.

### Every `simulate()` that shrinks or disappears

| Class | Today | After |
|---|---|---|
| `MotorStack` | 7 lines: read `angle.value`, raise if unbound, a loop of four `rotate` calls, one hand-inverted `rotate` | **gone** |
| `CenterStack` | 5 lines: read, raise, two `rotate` calls (one hand-inverted) | **gone** |
| `OutputStack` | 4 lines: read, raise, one `rotate` | **gone** |
| `TensionerStack` | 4 lines: read, raise, one `rotate` | **gone** |
| `ActuatorModuleV1` | 10 lines: three derived angles, seven bindings | **gone** — the driver reaches the train through relation 1 |

No `simulate()` and no port is left in the module. `ActuatorModuleV1` has
no subclass in this project (the two test classes are `TestCase` and
`ScenarioTest`, not node subclasses), so the OpenTorque caveat about
relations being additive through inheritance does not apply: the driver
may be the source of relation 1 rather than being bound in a `simulate()`.

### The frame arithmetic that leaves

Two hand inversions go, both written out today with a comment explaining
them:

- `MotorStack.simulate()`: `self.pulley.rotate(self.angle.value, (0, 1, 0))`
  — "Motion is composed inside rest placement; this STEP's native axis is
  +Y". Joint 1 states the machine axis in the root's frame; the framework
  carries it through the pulley's `rotate(90, (1, 0, 0))` itself.
- `CenterStack.simulate()`: the same line for `self.pinion`. Joint 3
  states `(0, 0, 1)` in the stack's frame; the framework produces the
  `(0, 1, 0)`.

Also gone, though never written: the reliance on innermost composition
that makes `self.codewheel_mount.rotate(angle, AXIS)` correct even though
the mount is placed 28.7 mm down the shaft. A reader had to know that rule
to know which line it turns about; joint 1 states the line.

## What does not change

- **Geometry and sources.** Every `StepNode`/`StlNode` source path,
  `color`, `angular_deflection`, every CadQuery envelope
  (`MotorRotorEnvelope`, `MotorStatorEnvelope`, `EncoderCodewheel`, the
  three bearings) and both molejo `Shape`s — profile, `Wrap`, `Teeth`,
  sample counts — byte for byte.
- **Placements.** Every `render()` is untouched: `CENTER_CENTER`,
  `OUTPUT_CENTER`, `TENSIONER_X/Y`, `FIRST_STAGE_Z`, `SECOND_STAGE_Z`,
  `SEATING_GAP`, the `-28.7` codewheel mount station, the two
  `rotate(90, (1, 0, 0))` pulley placements.
- **Node paths and the tree shape.** No node is added, removed, renamed or
  re-parented, so `seats.py`'s `KNOWN_RIGID_OVERLAPS` key
  `("center_stack.gear", "center_stack.pinion")` and every path a test
  walks stay as they are. In particular the bearings stay where they are
  and stay STILL: `center_stack.lower_bearing`, `upper_bearing`,
  `output_stack.lower_bearing`, `upper_bearing` and both
  `tensioner.bearing` nodes have no joint and are named by no relation, so
  their world matrices are unchanged at every pose. (Rejected alternative:
  one joint per stack, which is fewer declarations but turns those six
  bearings and so changes six matrices at every non-zero pose.)
- **Control surface.** One driver `input_angle` (default 0.0, range
  0..3240°, deg) and the three instructions `Home`, `Inspect Reduction`,
  `One Output Turn`, with the same targets and durations. Joints are
  ports, not drivers, so the driver table stays exactly `["input_angle"]`
  and `openspec/specs/dual-stage-belt-drive/spec.md` keeps its meaning
  unchanged.
- **Poses.** Identical at every pose, to the 1e-9 the pose harness
  compares at (see "On exactness" above).
- **Contracts and tests.** `simulation/seats.py`, every assertion in
  `simulation/test_actuator.py`, and `simulation/tools/probe.py` — no test
  edit is proposed (see **Tests**).
- **The rest of the repository.** `pyproject.toml`, the declared model
  `actuator-module-v1`, `README.md`, `docs/measurements.md`, the two
  ratified spec files under `openspec/specs/`, and every upstream
  `mechanics/` and `electronics/` file. This change adds no spec delta:
  the behaviour the two specs state is exactly preserved.

## Known gaps

No motion in this machine has to stay hand-written, and no primitive is
missing for it. Two of the three known 2026-09-09 limits are met as
friction, not as blockers, and are worth recording as further sightings:

1. **A relation chain must be stated in one class body** (limit 2 of the
   2026-09-09 group; OpenTorque's sighting (a)). The press fit of relation
   3 is `CenterStack`'s own knowledge and wants to be written in
   `CenterStack`'s class body as `gear.spin.drives(pinion.spin)`. It
   cannot be: `CenterStack`'s relations solve AFTER its parent's, so the
   root's relation 4 would find `center_stack.pinion.spin` unbound and
   raise `UnreachedCoordinate`. All eight sentences therefore sit in the
   root, including the one about two children of one child. Nothing is
   lost but locality.
2. **A joint's anchor cannot say "my own placed origin"** (limit 1 of
   2026-09-09; the declaration-site finding). Joints 4 and 5 write
   `at=(0, 0, SECOND_STAGE_Z)`, which is exactly the `translate` their
   parent's `render()` already applied — the number twice. Writing
   `at=(0, 0, 0)` instead would be geometrically identical (a z line
   through the frame origin is the same line) but would emit two centring
   translations per bind instead of one clean rotation. The
   own-placed-origin anchor mode already proposed would remove both `at`s.
   Milder than in the sibling projects: every joint-bearing class here is
   used at exactly one placement — `TensionerRoller` twice, but at the
   same placement inside two identical stacks — so no class is subclassed
   just to carry a joint and no parent's layout constant is dragged into a
   part module.
3. Limit 3 (a node's own derived coordinate is unbound inside its own
   `simulate()`) is not met at all: there are no derived coordinates and
   no `simulate()` left.
4. Not met either: composition order (no body has two joints), the orbit
   primitive (no carried body — there is no planetary stage in this
   machine), fan-out over `.repeat()` or list-held children (nothing is
   repeated), multi-source relations (every relation has one source), and
   the `Length()` wrap (no dimensioned tokens in this simulation).

One implementation risk, not a framework gap: the belt ports are now bound
at the END of the root's simulate phase, by the relation solve, instead of
during `simulate()`. If a `MolejoNode` were to read its port before the
solve, the belts would lag one instant.
`test_belts_circulate_with_input` is the test that would catch it, and the
pose comparison covers it at every pose; if either shows it, stop and
report rather than reintroducing a binding in `simulate()`.

## Pre-existing state

- The repository is on branch `master`, clean: `git status --porcelain`
  is empty at `87c49e5` ("feat(simulation): add actuator module v1
  model"). There is **no stage 0 commit** to make. `_build/`,
  `_build.lock`, `__pycache__/` and the three `snapshot-*.png` /
  `screenshot.png` files are left exactly as they are.
- **The project does NOT run on the current framework**, contrary to the
  tracker's "imports not broken" note. The single import
  `import simulation.actuator` raises `ImportError` from
  `solid_node/node/__init__.py` naming `RotationalPort` and pointing at
  `solid_node.motion.ports`. `simulation/actuator.py` is the only module
  affected; `AssemblyNode`, `CadQueryNode`, `MolejoNode`, `StepNode` and
  `StlNode` still come from `solid_node.node`, and `ScenarioTest`,
  `TestCase` and `StepAssembly` are all still where the project imports
  them from (checked by importing each).
- Consequently there is no known-good baseline for this project on this
  framework tree: stage A establishes it. No test has been run by this
  proposal.

## Tests

`simulation/test_actuator.py` is the whole suite: twelve tests in
`ActuatorModuleV1Test` (run by `solid test` against the declared model)
and one scenario test in `ActuatorModuleV1ScenarioTest`. There is no plain
`pytest` suite. None of them reads a port that this change removes —
checked by grep: the string `angle` appears in the tests only as
`input_angle` (the driver, which stays) and as the local `angle_degrees`
of the rotation helper.

| Test | What it asserts | Expected effect |
|---|---|---|
| `test_motor_stack_axes_are_coaxial` | shaft, pulley, mount centred on x=y=0 | unchanged; it is also the evidence for joint 1's axis |
| `test_motor_shaft_uses_source_dimensions` | 3.99 mm × 33.4 mm from the STEP | unchanged (geometry untouched) |
| `test_motor_source_solids_are_connected` | no disconnected solids in the motor stack | unchanged; kernel-dependent at baseline |
| `test_documented_shaft_stations` | 0 / 43.9 / 113.8 mm stations | unchanged; the evidence for the joint anchors |
| `test_center_stack_is_coaxial` | pinion and gear on 43.9 | unchanged; evidence for joints 2 and 3 |
| `test_output_bearings_are_coaxial` | pulley and both bearings on 113.8 | unchanged; also the reason the bearings may stay still |
| `test_belts_use_documented_sizes` | 50/67 teeth, 3.0 pitch, 4/6 mm width, read off `render().to_dict()` | unchanged; the belt ports keep their names |
| `test_documented_centers_close_nominal_belts` | pure `layout.py` arithmetic | unchanged; `layout.py` only GAINS constants |
| `test_belts_circulate_with_input` | belt vertices move by >0.1 mm between `input_angle` 0 and 90 | unchanged, and the guard against the relation-timing risk above |
| `test_rigid_stacks_follow_two_stage_reduction` | at 810°: motor pulley +810°, centre gear +270° about (43.9, 0), output pulley +90° about (113.8, 0), `atol=0.02` | unchanged. This is the test that proves relations 2 and 4; its tolerance is 2e-2, far above the ~1e-13 ulp difference between `x/3.0` and `x*(10/30)` |
| `test_solid_integrity` | no disconnected solids in the whole tree | unchanged; kernel-dependent at baseline |
| `test_assembly_integrity` | the set of interfering rigid pairs equals `KNOWN_RIGID_OVERLAPS` exactly | unchanged in intent; kernel-dependent at baseline (see below) |
| `test_known_center_press_fit_volume` | the gear/pinion overlap is between 0.08 and 0.13 mm³ | unchanged in intent; kernel-dependent at baseline (see below) |
| `ActuatorModuleV1ScenarioTest::test_instructions_land_exactly` | the three instructions land on 810 / 3240 / 0 exactly, with the interference inventory checked every 1.5 s | unchanged: instructions and driver are untouched |

**Tests I expect to need a change: none.** No assertion names a removed
port, no node path changes, and no tolerance in the suite is tighter than
the arithmetic difference this change introduces.

**Tests I flag as at risk at the BASELINE, for reasons that are not
motion** — the orchestrator decides, I only flag:

- `test_assembly_integrity` and `test_known_center_press_fit_volume`
  measure boolean intersection VOLUMES (0.10472716970402911 mm³ measured,
  bounded at 0.08–0.13). Sibling projects in this campaign hit
  faceted-epsilon noise on sub-mm³ interferences, and this project's
  measured value was recorded on 2026-09-07 under whatever kernel was
  current then. If either is red at stage A it is red before any motion
  work and must stay red, not be "fixed".
- `test_solid_integrity` and `test_motor_source_solids_are_connected`
  assert connectedness of imported STL/STEP bodies, the same class of
  check that is red at baseline in fender-bender and HACKberry.
- `README.md` documents both `--faceted` and `--exact` runs; the campaign
  protocol is faceted-first, and the exact kernel is not required for this
  refactor's evidence.
