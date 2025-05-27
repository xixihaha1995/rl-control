### Learning From Sinergym

#### Github Critical Concurrency Design
https://doi.org/10.1016/j.apenergy.2024.125046
https://gymnasium.farama.org/api/env/
https://github.com/ugr-sail/sinergym
https://github.com/intelligent-environments-lab/CityLearn
    https://docs.python.org/3/library/queue.html#queue.Queue.put
    https://github.com/ugr-sail/sinergym/blob/4ae5986c5130eb485c81cc0fefaaa12ac1bce769/sinergym/simulators/eplus.py#L182
    https://github.com/ugr-sail/sinergym/blob/4ae5986c5130eb485c81cc0fefaaa12ac1bce769/sinergym/simulators/eplus.py#L149
    https://github.com/ugr-sail/sinergym/blob/4ae5986c5130eb485c81cc0fefaaa12ac1bce769/sinergym/simulators/eplus.py#L153
    https://github.com/ugr-sail/sinergym/blob/4ae5986c5130eb485c81cc0fefaaa12ac1bce769/sinergym/envs/eplus_env.py#L284
    https://github.com/ugr-sail/sinergym/blob/4ae5986c5130eb485c81cc0fefaaa12ac1bce769/sinergym/envs/eplus_env.py#L371
    https://github.com/ugr-sail/sinergym/blob/4ae5986c5130eb485c81cc0fefaaa12ac1bce769/sinergym/envs/eplus_env.py#L373
    Truncated/complete: https://github.com/ugr-sail/sinergym/blob/4ae5986c5130eb485c81cc0fefaaa12ac1bce769/sinergym/simulators/eplus.py#L167
    Truncated/complete: https://github.com/ugr-sail/sinergym/blob/4ae5986c5130eb485c81cc0fefaaa12ac1bce769/sinergym/envs/eplus_env.py#L359
        - truncated (bool) – Whether the truncation condition outside the scope of the MDP is satisfied. 
            Typically, this is a **timelimit**, but could also be used to indicate an agent physically going out of bounds.
        - Reward should be generally set as negative 
            (except final goal is achieved, but building resource efficient control is not goal-oriented), 
            so no intermediate termination/truncation will be triggered.
        - reset() - Resets the environment to an initial state, required **before** calling step

#### My Own Concurrency Implementation
Co-simulation with EnergyPlus:
- Thread(target=run_vcwg).start()
- coordination.ep_api.runtime.run_energyplus(state, sys_args)
- is model.learn(), model.predict() calling the same _init_() of custom env class?
- reward/constraints (Zone Air Temperature Violation, Chiller Electricity Rate and Accumalated Energy Consumption, etc.)
  - Correct, and generally reward should be set as "negative" for building control.
- action = model.predict(obs)
- obs, reward, done, info = env.step(action)

sem0.acquire(), RL.get_initial_action, sem1.release()
    sem1.acquire, eplus.after_predictor_after_hvac_managers, eplus.end_system_timestep_after_hvac_reporting, sem2.release()
sem2.acquire(), RL.from_obsReward_to_next_action, sem0.release()

Handle exceptions:
    -RL.reset > EPlus.reset
    -EPlus.run_outOf_loop > env.terminate()

### RL-EPlus Software Development

#### Reference
https://doi.org/10.1016/j.apenergy.2024.125046
VAV Box, VAV Damper Signal, discharge air mass flow rate
Chilled Water, Chiller Supply Water Temperature, range between 4 to 15°C
Chilled Water, Cooling Coil Valve Signal / Chiller Valve Position, range between 0 to 1 with 0.1 increments
Air, Fan speed RPM Signal
Air, Economizer Damper Signal, Regulating mixed air temperature, range between minimum for adequate air quality, maximum

#### Incremental Development
observations: time (24 hours, weekday), odb, diffuse, direct, wind speed, wind direction, 
    zat, chiller electricity
actions (initial sensor values or ranges and policy setting values): CENTRAL CHILLER OUTLET NODE (temperature)

- ✅guess one number
- ❌guess 5 number sequence (time series)
https://github.com/Farama-Foundation/Gymnasium/tree/main/gymnasium/envs/classic_control

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

### Archived Theory Learning Notes

https://github.com/Farama-Foundation/Gymnasium/tree/main/gymnasium/envs/classic_control
https://stable-baselines3.readthedocs.io/en/master/modules/ddpg.html
https://github.com/openai/spinningup
https://github.com/DLR-RM/rl-trained-agents/blob/master/ddpg/AntBulletEnv-v0_1/AntBulletEnv-v0/config.yml
http://github.com/IBM/rl-testbed-for-energyplus
https://github.com/airboxlab/rllib-energyplus
https://github.com/ray-project/ray
https://docs.ray.io/en/latest/rllib/rllib-env.html

q*(a), the expected value of the action a.
Q(a), sample average method, the average of the rewards received after taking action a.
Q-learning, the action-value function is updated using the Bellman equation. (critics, as compared to policy, which is actors)

Twin Delayed DDPG (TD3), addressing function approaximation error in Actor-Critic methods.
..careful instruction on how to connect algorithm theory to algorithm code

On-policy (mathematically works out)
- Learning from data generated by the current policy
- Vanilla Policy Gradient, Trust Region Policy Optimization, Proximal Policy Optimization
- No old data
- VPG stability, but bad sample efficiency (progression is made from VPG to TRPO to PPO)

Off-policy (data strategy)
- Learning from data generated by a different policy (behavior policy vs target policy)
- Deep Deterministic Policy Gradient (DDPG), Twin Delayed DDPG (TD3), Soft Actor-Critic (SAC)
- Deep Q-Networks (DQN), Q-learning
- Can use old data, replay buffer is a memory of past experiences
- More sample efficient, but less stable (progression is made from DDPG to TD3 to SAC)

Total Time Steps in Enviroment (RL algos)
- The goal of the agent is to maximize its **cumulative reward**, called return.
- maximize some notion of **cumulative reward over a trajectory**
- Let's say you have an environment with more than 1000 timesteps
- you know how many timesteps the environment should last (i.e CartPole)