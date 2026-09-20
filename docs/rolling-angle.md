# Rolling-angle migration evidence

The two belt tensioners still turn against belt travel at their measured
5 mm roller radius. `TENSIONER_DEG_PER_MM` now states the distance-to-angle
conversion as `-rolling_angle(1.0, TENSIONER_ROLLER_RADIUS)`; the leading
minus sign, roller datum, belt ratios, and controls are unchanged.

The clean baseline was `master` at
`4b2c01d3d37b46ab44e67c30ba0046137779e7fd`. From the project root, every
command used:

```sh
export PYTHONPATH="$PWD:/home/asa/devel/machinome-studio/WTs/mechanics-rolling-angle"
```

with `/home/asa/devel/machinome-studio/.venv/bin/python` or
`/home/asa/devel/machinome-studio/.venv/bin/machinome`. The baseline Python
probe reported radius 5.0 mm and -11.459155902616464 degrees/mm; belt travels
-25, -1, 0, 1, and 12.5 mm produced tensioner angles 286.4788975654116,
11.459155902616464, -0.0, -11.459155902616464, and
-143.2394487827058 degrees. The pre-edit faceted suite passed 14/14.

After the edit, the Python probe compared the old expression and
`-rolling_angle(travel, radius)` at those same travels. A supported raw
deferred input, `solid2.get_animation_time() * 12.5`, produced the deferred
angle expression `-(($t * 12.5) / 5.0) * 57.29577951308232`; its samples at
`$t = 0` and `$t = 1` are the same -0.0 and -143.2394487827058 degrees as the
numeric relation. These commands then passed:

```sh
/home/asa/devel/machinome-studio/.venv/bin/machinome test --faceted simulation/actuator.py
/home/asa/devel/machinome-studio/.venv/bin/machinome test --exact simulation/actuator.py
/home/asa/devel/machinome-studio/.venv/bin/machinome build
/home/asa/devel/machinome-studio/.venv/bin/machinome snapshot -o /tmp/actuator-angle-rest.png --autocenter
/home/asa/devel/machinome-studio/.venv/bin/machinome snapshot -o /tmp/actuator-angle-810.png --autocenter --drive input_angle=810
```

The faceted and exact suites each passed 14/14, the build succeeded, and both
snapshot files were created. Visual inspection found the same continuous
belt routes and tensioner roller poses at rest and at 810 input degrees; the
center/output stages retained their datums. Snapshots do not prove tooth
contact, tension, or elasticity.

The mechanics worktree's base planning commit was
`c3665fc61291c895eb7719fbdc3c8fd274ec9e26`; it did not yet contain
`rolling_angle`. The uncommitted `machinome_mechanics/rolling.py` actually
tested had SHA-256
`14a09ea6cee1c4af3aa2716242523253ad8b234154b4f68d6cac43868849664e`, verified
locally with `sha256sum`. A final faceted-suite check was
bracketed by dependency readings: framework HEAD was
`0ce71cdea6cc4a2e7fd7e85dc68847daef3d34cc` before and after, and viewer HEAD
was `c6df93ddd1723f1b9be0fb7e73f19d6f6c2daffa` before and after. That check
passed 14/14. The framework had advanced concurrently to that retained-time
commit during the broader validation window; it was not changed or pinned by
this project work, so this records dependency drift rather than claiming one
immutable environment.
