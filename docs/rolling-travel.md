# Rolling-travel migration evidence

The actuator's ten-tooth pinion still advances each belt at its pitch circle.
`PITCH_ARC_PER_DEGREE` now names that established relation through
`machinome_mechanics.rolling_travel(1.0, PINION_PITCH_RADIUS)`; the pinion
radius, signs, drive ratios, and tensioner inverse conversion are unchanged.

The baseline on `master` at `52945759b57ec7ba40b3630ac9d861914906f2c0`
reported a 4.7746482927568605 mm pitch radius and 0.08333333333333333 mm per
degree. Representative angles -360, -45, 0, 90, and 810 degrees produced
-30, -3.75, 0, 7.5, and 67.5 mm. The pre-edit faceted actuator suite passed
14/14.

Validation ran from the project root with this environment prefix:

```sh
export PYTHONPATH="$PWD:/home/asa/devel/machinome-studio/WTs/mechanics-rolling-travel"
```

The executables were `/home/asa/devel/machinome-studio/.venv/bin/python` and
`/home/asa/devel/machinome-studio/.venv/bin/machinome`; the latter ran
`test --mesh simulation/actuator.py`, `test --brep
simulation/actuator.py`, `build`, and these two snapshot commands:

```sh
/home/asa/devel/machinome-studio/.venv/bin/machinome snapshot -o /tmp/actuator-rest.png --autocenter
/home/asa/devel/machinome-studio/.venv/bin/machinome snapshot -o /tmp/actuator-810.png --autocenter --drive input_angle=810
```

The Python comparison evaluated the old multiplication and `rolling_travel`
at -360, -45, 0, 90, and 810 degrees. Both returned, to floating-point
precision, -30, -3.75, 0, 7.5, and 67.5 mm; `rolling_travel(Angle(), radius)`
also produced a symbolic angle formula. The faceted suite passed 14/14 and
the exact suite passed 14/14. The build succeeded. Both snapshot files were
created; visual inspection found the two belts continuously routed around
their documented stacks at rest and with the center/output stages turned at
810 input degrees, with no pose or datum change.

The second `PYTHONPATH` entry is the independent machinome-mechanics
`mechanics-rolling-travel` worktree. This change does not migrate
`TENSIONER_DEG_PER_MM`: it is the inverse distance-to-angle operation reserved
for a separate helper. Snapshot inspection checks pose and belt routing, not
tooth contact or belt elasticity.
