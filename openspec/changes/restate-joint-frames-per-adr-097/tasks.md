# Tasks

Behaviour-preserving except for the one bug ADR-097's own-frame rule
fixes (`CenterPinion.spin`'s axis, wrong on main until this change).
Repository was clean at `565e966` before this change (only this change's
own new `openspec/changes/` directory and the edited `simulation/actuator.py`
are touched).

- [x] 1. Confirm `git rev-parse --show-toplevel` names this repository and
      `git status --porcelain` is clean before editing.
- [x] 2. Run the faceted suite on main, unedited, to record the
      consequence of the early ADR-097 merge.
      **Result:** 13/14 passed, 1 failed —
      `test_instructions_land_exactly`, extra interference pair
      `('center_stack.lower_bearing', 'center_stack.pinion')` beyond
      `KNOWN_RIGID_OVERLAPS`.
- [x] 3. Apply the three edits in `simulation/actuator.py`:
      `CenterPinion.spin` axis `(0, 0, 1)` → `(0, 1, 0)`; delete the
      restating `at=(0, 0, SECOND_STAGE_Z)` on `OutputPulley.spin` and on
      `TensionerRoller.spin`.
      **Result:** applied exactly as the framework cycle's
      `patch_open_robot_actuator_hardware.py` derived it.
- [x] 4. Run the faceted suite again.
      **Result:** 14/14 passed.
- [x] 5. Capture AFTER poses on main
      (`open_robot_actuator_hardware-actuator-module-v1-after.json`) and
      compare against the framework cycle's BEFORE file (captured on the
      pre-ADR-097 framework from the untouched source).
      **Result:** max deviation 0.000e+00 over 7 poses, 19 leaves.
- [x] 6. Run the exact suite.
      **Result:** 14/14 passed.
- [x] 7. Write this proposal and these tasks; do not archive (the
      orchestrator reviews first).
