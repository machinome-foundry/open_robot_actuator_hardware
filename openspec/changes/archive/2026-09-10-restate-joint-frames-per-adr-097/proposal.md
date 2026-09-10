# Restate joint frames for ADR-097 (joint-frame-follows-declarer)

## Why

solid-node main (91c0b2a) integrated `joint-frame-follows-declarer`
(ADR-097): a class-body joint's `axis`, `at` and `carries` are now read in
the DECLARING BODY'S OWN REST FRAME, not the parent's. `at` defaults to the
body's own origin. This project was migrated onto the motion layer in the
prior stage (`archive/2026-09-09-move-onto-motion`), which stated every
joint in the PARENT's frame as that framework required at the time. Two of
its five joints are now wrong on main:

- `CenterPinion.spin`'s axis `(0, 0, 1)` was correct only in
  `CenterStack`'s frame, before `CenterStack.render()`'s
  `self.pinion.rotate(90, (1, 0, 0))` is applied. Read in `CenterPinion`'s
  own rest frame it now names the wrong physical line, which is not a
  cosmetic difference: running the faceted suite on main before this
  change reproduces the consequence exactly —
  `test_instructions_land_exactly` fails because
  `center_stack.pinion` no longer only overlaps `center_stack.gear` (the
  documented press fit) but also `center_stack.lower_bearing`, since the
  pinion now spins about the wrong line.
- `OutputPulley.spin` and `TensionerRoller.spin` each wrote
  `at=(0, 0, SECOND_STAGE_Z)`, which is exactly the translation their
  parent (`OutputStack.render()` / `TensionerStack.render()`) already
  applies to place them. Under the new convention that restatement is
  applied twice.

`CenterGear.spin` and `MotorStack.turn` need no change: both bodies sit at
an identity placement under their parent (no `.translate()`/`.rotate()`
call touches them), so the parent's frame and their own rest frame already
coincide.

This is stage B of the campaign tracked at
`libresolid-studio/docs/motion-general-refactor.md`; the archived framework
change `solid-node/openspec/changes/archive/2026-09-10-joint-frame-follows-declarer/`
(`evidence/survey.md` §1.1) is the survey this proposal implements.

## What changes

`simulation/actuator.py`, three joint declarations, no other file:

1. `CenterPinion.spin`: `axis=(0, 0, 1)` → `axis=(0, 1, 0)`, derived as
   `R_rest^T . old_axis` for `R_rest` = "rotate 90° about `(1, 0, 0)`" (the
   parent's placement of `pinion`), computed exactly (90° rotations land on
   axis permutations, no floating-point residue).
2. `OutputPulley.spin`: `at=(0, 0, SECOND_STAGE_Z)` deleted (defaults to
   `(0, 0, 0)`, now correct in `OutputPulley`'s own rest frame).
3. `TensionerRoller.spin`: `at=(0, 0, SECOND_STAGE_Z)` deleted, same
   reasoning.

`CenterGear.spin` and `MotorStack.turn` are unchanged: both are
own-origin-already (identity parent placement).

No geometry, placement, port, driver, instruction, or test changes. No
spec delta: `openspec/specs/actuator-core-assembly/spec.md`'s "parallel to
+Z" claim describes the physical (post-placement) axis, which this change
preserves exactly — only the own-frame literal used to reach that same
physical axis changes.

## Evidence

- Faceted suite on main, before this change: 13/14 passed, 1 failed
  (`test_instructions_land_exactly`, extra interference
  `center_stack.pinion`/`center_stack.lower_bearing`) — this is the
  predicted consequence of the early framework merge, reproduced.
- Faceted suite after: 14/14 passed.
- Exact suite after: 14/14 passed.
- Pose comparison: `capture_poses.py compare` of the pre-change BEFORE
  file (captured by the framework cycle on the pre-ADR-097 framework, from
  the untouched source) against an AFTER file captured on main with this
  change applied: **max deviation 0.000e+00 over 7 poses, 19 leaves.**

## Known gaps

None found specific to this project's joints beyond what the archived
framework change and the campaign tracker already record. The rule stated
this project's five joints exactly; no sentence was unreachable.
