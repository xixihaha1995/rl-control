import numpy as np
import gymnasium as gym
from gymnasium.envs.registration import register

register(
    id='LichenEPlusRL-demo-v1',
    entry_point='LichenEPlusRL.EPlus_1_Env:EplusEnv',
    kwargs={
        'time_variables': ['month', 'day_of_month', 'hour'],
        'variables': {
            'outdoor_temperature': (
                'Site Outdoor Air DryBulb Temperature',
                'Environment'),
            'htg_setpoint': (
                'Zone Thermostat Heating Setpoint Temperature',
                'SPACE5-1'),
            'clg_setpoint': (
                'Zone Thermostat Cooling Setpoint Temperature',
                'SPACE5-1'),
            'air_temperature': (
                'Zone Air Temperature',
                'SPACE5-1'),
            'air_humidity': (
                'Zone Air Relative Humidity',
                'SPACE5-1'),
            'HVAC_electricity_demand_rate': (
                'Facility Total HVAC Electricity Demand Rate',
                'Whole Building')
        },
        'meters': {},
            }
        )