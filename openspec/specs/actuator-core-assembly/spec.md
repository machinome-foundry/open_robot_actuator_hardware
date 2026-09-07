# actuator-core-assembly Specification

## Purpose

Define the source-faithful geometry, documented shaft layout, component interfaces, and honest scope boundary of the reusable Brushless Actuator Module Core v1 simulation.

## Requirements

### Requirement: Source-faithful actuator parts
The simulation SHALL import every supplied v1 transmission part it represents from the repository's STEP or STL source without modifying that source, and SHALL distinguish drawn catalogue/reference hardware from supplied production geometry.

#### Scenario: Production geometry changes upstream
- **WHEN** a represented STEP or STL source changes
- **THEN** the next actuator build uses the changed source and the retained probe reports its current body and bounds evidence

### Requirement: Documented shaft layout
The simulated motor, center, and output axes SHALL be parallel to +Z, with the center axis 43.9 mm from the motor axis and the output axis 69.9 mm from the center axis.

#### Scenario: Actuator is built at home
- **WHEN** the actuator is built at `input_angle = 0 degrees`
- **THEN** geometry measurements locate the three axes at `(0, 0)`, `(43.9, 0)`, and `(113.8, 0)` millimetres within 0.02 mm

### Requirement: Coaxial component stacks
The motor pulley and shaft, the center pinion and 30-tooth pulley, and the output pulley and its two reference bearings SHALL each share one axis. The rigid-part interference inventory SHALL contain exactly the documented center pinion/gear press fit, bounded from 0.08 through 0.13 mm³, and no other positive-volume overlap.

#### Scenario: Core stack is assembled
- **WHEN** the actuator core is built
- **THEN** contracts prove each stack is coaxial, every rigid piece is one connected body, and the exact interference inventory contains only the bounded center pinion/gear press fit

### Requirement: Honest reusable-core boundary
The simulation SHALL identify the robot-specific structural shell, force and torque behaviour, belt preload, electronics, and manufacturing certification as outside the actuator-core model.

#### Scenario: Builder reads the simulation instructions
- **WHEN** the builder opens the project README
- **THEN** the documented model limits do not claim that a robot shell or physical performance has been simulated
