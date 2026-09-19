# Actuator Module Core v1 simulation measurements

These readings are evidence for the additive `simulation/` layer. They do not
modify or repair the upstream CAD. Reproduce the source inventory from the
repository root with:

```sh
PYTHONPATH="$PWD" /home/asa/devel/machinome-studio/.venv/bin/python -m simulation.tools.probe
```

## Documented layout

| Reading | Value | Source |
| --- | ---: | --- |
| Motor to center shaft | 43.9 mm | `mechanics/actuator_module_v1/images/transmission_1.png` |
| Center to output shaft | 69.9 mm | `mechanics/actuator_module_v1/images/transmission_1.png` |
| Stage ratio | 10:30 teeth (3:1) | Actuator v1 README |
| First belt | AT3, 150 mm, 50 teeth, 4 mm wide | Actuator v1 README and assembly instructions |
| Second belt | AT3, 201 mm, 67 teeth, 6 mm wide | Actuator v1 README and assembly instructions |
| Output bearings | 32 x 25 x 4 mm | Actuator v1 README |
| Center/motor bearings | 8 x 4 x 2 mm | Actuator v1 README |
| Tensioner bearings | 7 x 3 x 3 mm | Actuator v1 README |
| Default tensioner roller | 10.0 mm diameter | Center-pulley preparation instructions |
| Motor rotor | 45 mm diameter | Actuator v1 README |
| Encoder codewheel | 25.56 mm OD, 7 mm ID | Encoder details |

Using the AT3 pitch radius `pitch * teeth / (2*pi)`, the documented center
distances produce ideal open-belt path lengths of 149.8855 mm and 201.1066 mm.
The differences from the purchased nominal lengths are -0.1145 mm and +0.1066
mm before installed tensioner deflection.

## Source-frame readings

All actuator STLs are watertight and single-body. The represented source files
read as follows:

| File | Native bounds in mm | Reading used by the model |
| --- | --- | --- |
| `encoder_codewheel_pwb_mount.STL` | `[-6,-6,-4.66]` to `[6,6,1.3]` | Axis already +Z |
| `transmission_belt_tensioner_roller_10.0mm.STL` | `[-5,-5,-2]` to `[5,5,2]` | Axis already +Z |
| `transmission_pulley_at3_t30_center.STL` | `[-15,-15,-0.5]` to `[15,15,7.1]` | Axis already +Z |
| `transmission_pulley_at3_t30_output.STL` | approximately `[-14.5,-14.5,-8.2]` to `[14.5,14.5,8.2]` | Axis already +Z |
| `motor_antigravity_4004_custom_shaft.STEP` | `[-1.995,-1.995,-33.4]` to `[1.995,1.995,0]` | One shaft solid on +Z |
| `transmission_pulley_at3_t10_motor.STEP` | `[-4.57,0,-4.4096]` to `[4.57,6.7,4.4096]` | Rotate +90 degrees about X to put +Y on +Z |
| `transmission_pulley_at3_t10_center.STEP` | `[-4.57,0,-4.4096]` to `[4.57,19,4.4096]` | Rotate +90 degrees about X to put +Y on +Z |

The center pinion's toothed faces span Y=2.5 through Y=16.5 in its native STEP
frame. With the printed center gear spanning Z=-0.5 through Z=7.1, the shared
origin leaves the pinion engaged in the printed gear and exposes its far end for
the second 6 mm belt stage, matching the section view and assembly sequence.

## Interpretive limits

The project does not ship one reusable core shell: each downstream robot owns
its surrounding structure. Motor body, bearing, and codewheel solids in the
simulation are therefore labelled reference envelopes. Only catalogue-backed
diameters and widths participate in dimensional contracts; their illustrative
axial placements do not claim production geometry.
