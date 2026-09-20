# Pulley pitch-radius migration evidence

The actuator's ten-tooth and thirty-tooth AT3 pitch radii now use
`machinome_mechanics.pulley_pitch_radius`. Tooth counts, 3 mm pitch, centers,
belt sizes, ratios, tensioner motion, and controls are unchanged. Independent
test arithmetic was not migrated.

The clean base was `master` at
`0efefe824b9099b8d3485ea77baeea5d640d0fc6`. Commands ran from the project
root with:

```sh
export PYTHONPATH="$PWD:/home/asa/devel/machinome-studio/WTs/mechanics-pulley-pitch-radius"
```

and the workspace executables `/home/asa/devel/machinome-studio/.venv/bin/python`
and `/home/asa/devel/machinome-studio/.venv/bin/machinome`. The pre-edit
probe returned 4.7746482927568605 mm and 14.32394487827058 mm, and the
faceted actuator suite passed 14/14.

The final Python probe compared the old formula and helper at `(teeth,
pitch)` values `(10, 3)`, `(30, 3)`, `(7, 2.5)`, and `(255, 2.001)`; all
matched exactly as Python floats. A supported deferred pitch
`solid2.get_animation_time() * 3` produced
`(10 * ($t * 3.0)) / 6.283185307179586`, whose endpoint samples are 0 and
4.7746482927568605 mm. Validation commands were:

```sh
/home/asa/devel/machinome-studio/.venv/bin/machinome test --faceted simulation/actuator.py
/home/asa/devel/machinome-studio/.venv/bin/machinome test --exact simulation/actuator.py
/home/asa/devel/machinome-studio/.venv/bin/machinome build
/home/asa/devel/machinome-studio/.venv/bin/machinome snapshot -o /tmp/actuator-pulley-rest.png --autocenter
/home/asa/devel/machinome-studio/.venv/bin/machinome snapshot -o /tmp/actuator-pulley-810.png --autocenter --drive input_angle=810
```

Faceted and exact suites each passed 14/14; build and both snapshots
succeeded. Visual inspection found unchanged belt routes, pulley/roller
stations, and reduction pose at rest and 810 input degrees. The overview
cannot prove tooth contact, tension, or elasticity.

The mechanics worktree base planning commit was
`4870f32379fc9e0c966a0466a7a84f1ce4743ae5`; it did not contain the tested
implementation. The uncommitted `machinome_mechanics/belts.py` code identity
was SHA-256
`63f8d30a19d36b2cc4504919d6e3b989df1c0092348ad4c1930b31adb4ea482d`.
Framework HEAD stayed `0ce71cdea6cc4a2e7fd7e85dc68847daef3d34cc`.
Viewer HEAD changed concurrently from
`5dcbf4d476ff0d34bb42fe13f9b799ebd8ec5852` to
`4355da1a7f64dacd7d86eb27dbdfdf7ced94598f` and its worktree was dirty with
unrelated retained-time work; this project neither changed nor pinned it.
