# Tasks

Behaviour-preserving throughout: the acceptance is that every leaf's
composed world matrix is unchanged at every pose, so evidence is captured
before the first refactoring edit and compared after the last. The
repository is clean on `master` at `87c49e5`, so there is no stage 0
commit.

Run everything from the project root with `PYTHONPATH=.` and the workspace
venv (`/home/asa/devel/libresolid-studio/.venv/bin/python`,
`/home/asa/devel/libresolid-studio/.venv/bin/solid`). Never run two suites
at once. **Never edit a test.** `proposal.md` flags no test edit as needed;
if a test blocks the work, stop, report the exact assertion, and wait for
the orchestrator.

Confirm `git rev-parse --show-toplevel` names this repository before every
commit. Nothing is pushed.

## 0. Pre-existing state

- [x] 0.1 Confirm `git rev-parse --show-toplevel` is this repository and
      `git status --porcelain` is empty on `master` at `87c49e5`. Record
      "clean, no stage 0 commit" here. Leave `_build/`, `_build.lock`,
      `__pycache__/`, `screenshot.png` and the three `snapshot-*.png`
      alone; the only untracked entry should be
      `openspec/changes/move-onto-motion/`, which travels with the stage A
      commit.

      **Result:** clean, no stage 0 commit. `git rev-parse --show-toplevel`
      names this repository; `git status --porcelain` was empty at
      `87c49e5` except the untracked `openspec/changes/move-onto-motion/`.

## 1. Stage A — baseline

- [x] 1.1 Fix imports ONLY. In `simulation/actuator.py`, split the single
      `from solid_node.node import (...)` so that `RotationalPort` and
      `TranslationalPort` come from `solid_node.motion.ports` and
      `AssemblyNode`, `CadQueryNode`, `MolejoNode`, `StepNode`, `StlNode`
      keep coming from `solid_node.node`. No other file imports a moved
      name (checked in the proposal). Change nothing else — not a
      placement, not a port, not a `simulate()`.
- [x] 1.2 Run the declared model's suite and record the per-test result —
      pass, fail, error, with the assertion — here. This is THE baseline;
      a red test here stays red.

          PYTHONPATH=. .venv/bin/solid test --faceted simulation.actuator:ActuatorModuleV1

      `pyproject.toml` declares one model, `actuator-module-v1 =
      simulation.actuator:ActuatorModuleV1`; there is no plain `pytest`
      suite in this project. Expect 13 tests
      (`ActuatorModuleV1Test` ×12, `ActuatorModuleV1ScenarioTest` ×1).
      Pay particular attention to the four flagged in `proposal.md` as
      kernel-dependent: `test_assembly_integrity`,
      `test_known_center_press_fit_volume`, `test_solid_integrity`,
      `test_motor_source_solids_are_connected`.

      **Result:** 14 tests, 14 passed, 0 failed (faceted kernel, volume
      epsilon 0 mm3). `ActuatorModuleV1Test` actually has 13 tests, not
      12 — the proposal miscounted; `ActuatorModuleV1ScenarioTest` adds 1.
      All 14 green, including the four flagged kernel-dependent tests
      (`test_assembly_integrity`, `test_known_center_press_fit_volume`,
      `test_solid_integrity`, `test_motor_source_solids_are_connected`).
      This is the baseline: 14/14 green.

- [x] 1.3 Capture poses:

          PYTHONPATH=. python <shop>/docs/motion-general-refactor/capture_poses.py \
              capture simulation.actuator:ActuatorModuleV1 \
              /tmp/open-robot-actuator-before.json /tmp/open-robot-actuator-poses.json

      with the extra pose file holding the three instruction targets that
      the range-derived poses do not already cover:

          [{"input_angle": 0.0}, {"input_angle": 810.0}, {"input_angle": 3240.0}]

      Record the pose count and leaf count here.

      **Result:** captured 10 poses (defaults, `input_angle@0.4`,
      `input_angle@1.0`, `time@0.25`, `time@0.5`, `time@0.75`, and the
      three named `extra` poses for the instruction targets), 19 leaves,
      to `/tmp/open-robot-actuator-before.json` (extra pose file at
      `openspec/changes/move-onto-motion/extra-poses.json`).

- [x] 1.4 Commit as `refactor(simulation): import ports from
      solid_node.motion`, with the baseline in the message body, together
      with this change directory.

      **Result:** commit `b828249`.

## 2. Stage B — the motion refactor

Every step is in `simulation/actuator.py` unless it says otherwise. Do
not touch any `render()`, any source path, any colour, `seats.py`, the
driver or the instructions.

- [x] 2.1 `simulation/layout.py`: add the four constants beside the
      geometry they come from, changing no existing value:

          STAGE_RATIO = PINION_TEETH / GEAR_TEETH
          PITCH_ARC_PER_DEGREE = PINION_PITCH_RADIUS * pi / 180.0
          TENSIONER_ROLLER_RADIUS = 5.0
          TENSIONER_DEG_PER_MM = -180.0 / (TENSIONER_ROLLER_RADIUS * pi)

      `pi` is already imported there. Nothing else in `layout.py` changes.

- [x] 2.2 Imports in `actuator.py`: add
      `from solid_node.motion.joints import Revolute`; drop
      `RotationalPort` (no longer used) and keep `TranslationalPort` for
      the two belts. Import the new constants from `.layout`. Drop
      `from math import pi` if nothing else in the module uses it.

- [x] 2.3 Declare the five joints exactly as tabled in `proposal.md`, none
      with a `range`:

          class MotorStack(AssemblyNode):
              turn = Revolute(axis=(0, 0, 1), unit='deg')

          class CenterGear(StlNode):
              spin = Revolute(axis=(0, 0, 1), unit='deg')

          class CenterPinion(StepNode):
              spin = Revolute(axis=(0, 0, 1), unit='deg')

          class OutputPulley(StlNode):
              spin = Revolute(axis=(0, 0, 1), at=(0, 0, SECOND_STAGE_Z), unit='deg')

          class TensionerRoller(StlNode):
              spin = Revolute(axis=(0, 0, 1), at=(0, 0, SECOND_STAGE_Z), unit='deg')

      `OutputPulley` and `TensionerRoller` carry the anchor because it is
      their own placed origin, so the joint emits one rotation and no
      centring translation; the other three take the default anchor.
      `AXIS` is
      still used by nothing else after this step; delete the module
      constant only if it is unreferenced.

      **Result:** all five joints declared exactly as tabled: `turn` on
      `MotorStack`, `spin` on `CenterGear`, `CenterPinion`, `OutputPulley`
      and `TensionerRoller`. `AXIS` deleted — unreferenced after this step.

- [x] 2.4 Delete `MotorStack.angle`, `CenterStack.angle`,
      `OutputStack.angle`, `TensionerStack.angle` and all four of those
      classes' `simulate()` methods, including their
      `raise ValueError(... must be bound ...)` guards. Every `render()`
      in those classes stays byte for byte.

      **Result:** all four ports and all four `simulate()` bodies deleted;
      every `render()` left byte for byte.

- [x] 2.5 Delete `ActuatorModuleV1.simulate()` entirely and state the
      eight relations in its class body, after the child declarations, in
      this order:

          input_angle.drives(motor_stack.turn)
          motor_stack.turn.drives(center_stack.gear.spin, ratio=STAGE_RATIO)
          center_stack.gear.spin.drives(center_stack.pinion.spin)
          center_stack.pinion.spin.drives(output_stack.pulley.spin, ratio=STAGE_RATIO)
          motor_stack.turn.drives(first_belt.travel, ratio=PITCH_ARC_PER_DEGREE)
          center_stack.pinion.spin.drives(second_belt.travel, ratio=PITCH_ARC_PER_DEGREE)
          second_belt.travel.drives(upper_tensioner.roller.spin, ratio=TENSIONER_DEG_PER_MM)
          second_belt.travel.drives(lower_tensioner.roller.spin, ratio=TENSIONER_DEG_PER_MM)

      The driver, the instructions and `render()` are untouched. Solving
      order is the framework's business: the whole train is one class
      body, driven from `input_angle`.

      **Result:** `ActuatorModuleV1.simulate()` deleted; the eight
      relations stated in the class body, in the proposed order, right
      after the child declarations and before `render()` (matching the
      poseidon reference's placement). `render()`, the driver and the
      instructions unchanged.

- [x] 2.6 Confirm by grep that no port removed in 2.4 is read anywhere
      (`simulation/`, `README.md`, `docs/`), that no node path changed,
      that `seats.py` is untouched, and that no `simulate()` and no
      `RotationalPort` is left in `simulation/`.

      **Result:** `grep -rn "def simulate" simulation/` — no matches.
      `grep -rn "RotationalPort" simulation/` — no matches.
      `grep -rn "\.angle\b" simulation/ README.md docs/` — no matches.
      `git diff --stat simulation/seats.py` — empty (untouched). No node
      path changed anywhere in the refactor.

## 3. Evidence again

- [x] 3.1 Re-capture to `/tmp/open-robot-actuator-after.json` with the
      same extra pose file and run

          python <shop>/docs/motion-general-refactor/capture_poses.py compare \
              /tmp/open-robot-actuator-before.json /tmp/open-robot-actuator-after.json

      Expected: **max deviation 0** over every pose, including the three
      instruction targets, and no problem lines. The four removed ports
      read `<absent>` after and are ignored by the comparison; the new
      joint coordinates appear only in the "after" file and are likewise
      ignored. A non-zero matrix deviation stops the work and is reported,
      not accepted — the ulp difference between `x / 3.0` and
      `x * STAGE_RATIO` is ~1e-13° and disappears in the harness's
      9-decimal rounding.

      **Result:** `max deviation 0.000e+00 over 10 poses`, no problem
      lines at all — not even a rounded-away ulp deviation.

- [x] 3.2 Run the same suite as 1.2 and compare with the baseline: the
      same tests green, none newly red, none skipped. Watch
      `test_rigid_stacks_follow_two_stage_reduction` (relations 2 and 4)
      and `test_belts_circulate_with_input` (the belt ports now bound by
      the relation solve rather than in `simulate()`) in particular.

      **Result:** 14 tests, 14 passed, 0 failed — identical to the
      baseline (same 14 tests, none newly red, none skipped), including
      `test_rigid_stacks_follow_two_stage_reduction` and
      `test_belts_circulate_with_input`.

- [x] 3.3 Record here: the pose comparison line, the test counts before
      and after, every deviation from the proposal and why, and any
      framework behaviour that contradicted it — in particular (a) whether
      a `Driver` as a relation source binds `motor_stack.turn` in the root
      with no `simulate()` present at all, (b) whether the two belt
      `TranslationalPort`s feeding molejo's `P.travel` see their value in
      time when a relation binds them at the end of the simulate phase,
      and (c) whether the `at=(0, 0, SECOND_STAGE_Z)` anchors do collapse
      to a single rotation.

      **Result:**
      - Pose comparison: `max deviation 0.000e+00 over 10 poses`, no
        problems.
      - Tests: 14/14 before, 14/14 after; no test changed, none newly red.
      - Deviations from the proposal: none. Implemented exactly as
        proposed and tasked — five joints (`MotorStack.turn`;
        `CenterGear.spin`, `CenterPinion.spin`, `OutputPulley.spin`,
        `TensionerRoller.spin`), eight relations in `ActuatorModuleV1`'s
        class body, four constants added to `layout.py`, four ports and
        five `simulate()` bodies (including the root's) removed, no joint
        `range`.
      - Framework behaviour, the three watch points: (a) yes — the
        `Driver.drives(motor_stack.turn)` relation binds `MotorStack.turn`
        with no `simulate()` anywhere in `MotorStack`; the pose comparison
        and `test_rigid_stacks_follow_two_stage_reduction` both confirm the
        bind lands correctly. (b) yes — both belts' `TranslationalPort`s
        see their relation-bound value in time for molejo's `P.travel`;
        `test_belts_circulate_with_input` passed and the belt leaf matrices
        matched at every pose, so no lag was observed. (c) yes — the
        `at=(0, 0, SECOND_STAGE_Z)` anchors on `OutputPulley.spin` and
        `TensionerRoller.spin` collapsed to a single rotation with no
        drift versus the hand-written `translate` + `rotate` they replace;
        max deviation is exactly 0, not merely under tolerance.

- [x] 3.4 Commit as `refactor(simulation): move the actuator module onto
      solid-node joints and couplings`, with the pose result and the test
      result in the body. Do NOT sync or archive this change; the
      orchestrator does that after review.

      **Result:** commit `1ab4f74`.

## Review (orchestrator, 2026-09-09)

Diff matches the reviewed proposal; poses bit-identical over 10 poses;
14/14 green before and after. Archived.
