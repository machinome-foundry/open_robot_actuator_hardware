## ADDED Requirements

### Requirement: One meaningful actuator control
The actuator SHALL expose one `input_angle` driver in degrees, ranging from 0 through 3240 degrees, and SHALL derive all internal rotations and belt travel from it.

#### Scenario: Builder moves the actuator input
- **WHEN** `input_angle` advances by 810 degrees
- **THEN** the motor stack advances 810 degrees, the center stack advances 270 degrees, and the output stack advances 90 degrees

### Requirement: Documented two-stage reduction
Each 10-tooth pulley SHALL drive its paired 30-tooth pulley as an open AT3 belt stage, producing a 3:1 reduction per stage and 9:1 total reduction without reversing direction.

#### Scenario: Input completes nine turns
- **WHEN** `input_angle` advances from 0 to 3240 degrees
- **THEN** the output pulley advances exactly 360 degrees in the same direction

### Requirement: Source-sized moving belts
The first and second stages SHALL show closed moving AT3 belts with 3 mm pitch, 50 and 67 teeth respectively, and documented widths of 4 mm and 6 mm.

#### Scenario: Transmission moves through an inspection pose
- **WHEN** the actuator moves from home to `input_angle = 810 degrees`
- **THEN** both belt paths remain closed on their pitch circles while their tooth phases advance with their driving pulleys

### Requirement: Small actuator demonstration
The actuator SHALL provide `Home`, `Inspect Reduction`, and `One Output Turn` instructions that ramp at the documented inspection rate and land exactly on their target input angles.

#### Scenario: Builder runs every instruction
- **WHEN** a scenario triggers `Inspect Reduction`, `One Output Turn`, and `Home` in sequence
- **THEN** each move completes at 810, 3240, and 0 input degrees respectively and sampled rigid-part integrity remains valid throughout
