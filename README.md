### Modelica

#### Reference
https://doi.org/10.1016/j.apenergy.2024.125046
VAV Box, VAV Damper Signal, discharge air mass flow rate
Chilled Water, Chiller Supply Water Temperature, range between 4 to 15°C
Chilled Water, Cooling Coil Valve Signal / Chiller Valve Position, range between 0 to 1 with 0.1 increments
Air, Fan speed RPM Signal
Air, Economizer Damper Signal, Regulating mixed air temperature, range between minimum for adequate air quality, maximum


#### General EPlus Question
SimulationControl,
    Yes,                     !- Do Zone Sizing Calculation
    Yes,                     !- Do System Sizing Calculation
    Yes,                     !- Do Plant Sizing Calculation
    No,                      !- Run Simulation for Sizing Periods
    Yes,                     !- Run Simulation for Weather File Run Periods
    No,                      !- Do HVAC Sizing Simulation for Sizing Periods
    1;                       !- Maximum Number of HVAC Sizing Simulation Passes

Why does this line matter, "Do HVAC Sizing Simulation for Sizing Periods"?


#### Incremental Development

observations: time (24 hours, weekday), odb, diffuse, direct, wind speed, wind direction, 
    zat, chiller electricity
actions (initial sensor values or ranges and policy setting values): CENTRAL CHILLER OUTLET NODE (temperature)

- ✅guess one number
- ❌guess 5 number sequence (time series)

#### Archived notes for IDF

SetpointManager:Scheduled,
    Central Chiller Setpoint Manager,  !- Name
    Temperature,             !- Control Variable
    CW Loop Temp Schedule,   !- Schedule Name
    Central Chiller Outlet Node;  !- Setpoint Node or NodeList Name

ConvergenceLimits,
    0,                       !- Minimum System Timestep {minutes}
    25;                      !- Maximum HVAC Iterations

callback_begin_system_timestep_before_predictor
    reduce lighting or process loads, change thermostat settings,
callback_after_predictor_before_hvac_managers
    the EMS control actions could be overwritten by other SetpointManager
✅callback_after_predictor_after_hvac_managers
    SetpointManager or AvailabilityManager actions may be overwritten by EMS control actions.
..before reporting
    custom output
callback_end_system_timestep_after_hvac_reporting
✅callback_end_zone_timestep_after_zone_reporting


    Space3-1
Space4-1 Space5-1 Space2-1 
    Space1-1

! Zone Description Details:
!
!      (0,15.2,0)                      (30.5,15.2,0)
!           _____   ________                ____
!         |\     ***        ****************   /|
!         | \                                 / |
!         |  \                 (26.8,11.6,0) /  |
!         *   \_____________________________/   *
!         *    |(3.7,11.6,0)               |    *
!         *    |                           |    *
!         *    |                           |    *
!         *    |               (26.8,3.7,0)|    *
!         *    |___________________________|    *
!         *   / (3.7,3.7,0)                 \   *
!         |  /                               \  |
!         | /                                 \ |
!         |/___******************___***________\|
!          |       Overhang        |   |
!          |_______________________|   |   window/door = *
!                                  |___|
!
!      (0,0,0)                            (30.5,0,0)

Object in IDF: 
- CENTRAL CHILLER OUTLET NODE
- MAIN COOLING COIL 1 WATER INLET NODE (MAIN COOLING COIL 1)
- SUPPLY FAN 1
- SPACE1-1 NODE
- SPACE3-1 NODE

Actuator,System Node Setpoint,Temperature Setpoint,CENTRAL CHILLER OUTLET NODE,[C]
Actuator,System Node Setpoint,Temperature Minimum Setpoint,CENTRAL CHILLER OUTLET NODE,[C]
Actuator,System Node Setpoint,Temperature Maximum Setpoint,CENTRAL CHILLER OUTLET NODE,[C]
Actuator,System Node Setpoint,Mass Flow Rate Setpoint,CENTRAL CHILLER OUTLET NODE,[kg/s]
Actuator,System Node Setpoint,Mass Flow Rate Maximum Available Setpoint,CENTRAL CHILLER OUTLET NODE,[kg/s]
Actuator,System Node Setpoint,Mass Flow Rate Minimum Available Setpoint,CENTRAL CHILLER OUTLET NODE,[kg/s]
OutputVariable,Chiller Electricity Rate,CENTRAL CHILLER,[W]
OutputVariable,Chiller Electricity Energy,CENTRAL CHILLER,[J]
Central Chiller Inlet Node,  !- Chilled Water Inlet Node Name
Central Chiller Outlet Node,  !- Chilled Water Outlet Node Name
OutputVariable,Chiller Evaporator Inlet Temperature,CENTRAL CHILLER,[C]
OutputVariable,Chiller Evaporator Outlet Temperature,CENTRAL CHILLER,[C]
OutputVariable,Chiller Evaporator Mass Flow Rate,CENTRAL CHILLER,[kg/s]

Actuator,System Node Setpoint,Temperature Setpoint,MAIN COOLING COIL 1 WATER INLET NODE,[C]
Actuator,System Node Setpoint,Temperature Minimum Setpoint,MAIN COOLING COIL 1 WATER INLET NODE,[C]
Actuator,System Node Setpoint,Temperature Maximum Setpoint,MAIN COOLING COIL 1 WATER INLET NODE,[C]
Actuator,System Node Setpoint,Mass Flow Rate Setpoint,MAIN COOLING COIL 1 WATER INLET NODE,[kg/s]
Actuator,System Node Setpoint,Mass Flow Rate Maximum Available Setpoint,MAIN COOLING COIL 1 WATER INLET NODE,[kg/s]
Actuator,System Node Setpoint,Mass Flow Rate Minimum Available Setpoint,MAIN COOLING COIL 1 WATER INLET NODE,[kg/s]
OutputVariable,Cooling Coil Total Cooling Energy,MAIN COOLING COIL 1,[J]

Actuator,Fan,Fan Air Mass Flow Rate,SUPPLY FAN 1,[kg/s]
Actuator,Fan,Fan Pressure Rise,SUPPLY FAN 1,[Pa]
Actuator,Fan,Fan Total Efficiency,SUPPLY FAN 1,[fraction]
Actuator,Fan,Fan Autosized Air Flow Rate,SUPPLY FAN 1,[m3/s]
OutputVariable,Fan Electricity Energy,SUPPLY FAN 1,[J]

Actuator,System Node Setpoint,Mass Flow Rate Setpoint,SPACE3-1 NODE,[kg/s]
Actuator,System Node Setpoint,Mass Flow Rate Maximum Available Setpoint,SPACE3-1 NODE,[kg/s]
Actuator,System Node Setpoint,Mass Flow Rate Minimum Available Setpoint,SPACE3-1 NODE,[kg/s]