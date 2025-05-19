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

#### Replication
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