import os, sys, datetime
sys.path.insert(0, '/usr/local/EnergyPlus-24-2-0/')
sys.path.insert(0, 'C:/EnergyPlusV24-2-0')
from pyenergyplus.api import EnergyPlusAPI

def get_zone_handles(state):
    global zone_names
    zone_names = ['SPACE1-1',
                  'SPACE2-1',
                  'SPACE3-1',
                  'SPACE4-1',
                  'SPACE5-1']

    zone_temp_c = []
    for zone in zone_names:
        _tmpRtemp = ep_api.exchange.get_variable_handle(state,
                                                   "Zone Air Temperature",
                                                   zone)
        if _tmpRtemp < 0:
            raise Exception("Error: Invalid handle for zone: "+zone)
        zone_temp_c.append(_tmpRtemp)

    return zone_temp_c

def get_building_handles(state):
    global allHandles
    allHandles = {}
    allHandles['sensor'] = {}
    allHandles['actuator'] = {}
    oat_c = ep_api.exchange.get_variable_handle(state,"Site Outdoor Air Drybulb Temperature",
                                                                             "Environment")
    direct_rad = ep_api.exchange.get_variable_handle(state,"Site Direct Solar Radiation Rate per Area",
                                                                                "Environment")
    diffuse_rad = ep_api.exchange.get_variable_handle(state,"Site Diffuse Solar Radiation Rate per Area",
                                                                                "Environment")
    wind_speed = ep_api.exchange.get_variable_handle(state,"Site Wind Speed","Environment")
    wind_dir = ep_api.exchange.get_variable_handle(state,"Site Wind Direction","Environment")
    #OutputVariable,Chiller Electricity Energy,CENTRAL CHILLER,[J]
    # ep_api.exchange.request_variable(state, "Chiller Evaporator Outlet Temperature", "CENTRAL CHILLER")
    # ep_api.exchange.request_variable(state, "Chiller Evaporator Mass Flow Rate", "CENTRAL CHILLER")

    vav1_damper_pos = ep_api.exchange.get_variable_handle(state,
                                                        "Zone Air Terminal VAV Damper Position",
                                                        "SPACE1-1 VAV Reheat")
    vav1_damper_pos_min = ep_api.exchange.get_variable_handle(state,
                                                        "Zone Air Terminal Minimum Air Flow Fraction",
                                                        "SPACE1-1 VAV Reheat")

    chiller_electricity = ep_api.exchange.get_variable_handle(state,"Chiller Electricity Energy",
                                                                    "CENTRAL CHILLER")
    chiller_evaporator_outlet_temp = ep_api.exchange.get_variable_handle(state,
                                                                    "Chiller Evaporator Outlet Temperature",
                                                                    "CENTRAL CHILLER")
    chiller_evaporator_outlet_temp_high = ep_api.exchange.get_variable_handle(state,
                                                                    "System Node Setpoint High Temperature",
                                                                    "CENTRAL CHILLER OUTLET NODE")
    chiller_evaporator_outlet_temp_low = ep_api.exchange.get_variable_handle(state,
                                                                    "System Node Setpoint Low Temperature",
                                                                    "CENTRAL CHILLER OUTLET NODE")
    chiller_evaporator_mass_flow_rate = ep_api.exchange.get_variable_handle(state,
                                                                    "Chiller Evaporator Mass Flow Rate",
                                                                    "CENTRAL CHILLER")
    '''
    Actuator,System Node Setpoint,Temperature Setpoint,CENTRAL CHILLER OUTLET NODE,[C]
    Actuator,System Node Setpoint,Temperature Minimum Setpoint,CENTRAL CHILLER OUTLET NODE,[C]
    Actuator,System Node Setpoint,Temperature Maximum Setpoint,CENTRAL CHILLER OUTLET NODE,[C]
    Actuator,System Node Setpoint,Mass Flow Rate Setpoint,SPACE1-1 NODE,[kg/s]
    '''
    chillerEvaporatorOutletTempAct = ep_api.exchange.get_actuator_handle(state,
                                                                    "System Node Setpoint",
                                                                    "Temperature Setpoint",
                                                                    "CENTRAL CHILLER OUTLET NODE")
    chillerEvaporatorOutletTempActMin = ep_api.exchange.get_actuator_handle(state,
                                                                    "System Node Setpoint",
                                                                    "Temperature Minimum Setpoint",
                                                                    "CENTRAL CHILLER OUTLET NODE")
    chillerEvaporatorOutletTempActMax = ep_api.exchange.get_actuator_handle(state,
                                                                    "System Node Setpoint",
                                                                    "Temperature Maximum Setpoint",
                                                                    "CENTRAL CHILLER OUTLET NODE")
    vav1MdotKgSAct = ep_api.exchange.get_actuator_handle(state,
                                                                    "System Node Setpoint",
                                                                    "Mass Flow Rate Setpoint",
                                                                    "SPACE1-1 NODE")

    #find if any of hanldes < -1, then raise exception
    _allHandles = [oat_c, direct_rad, diffuse_rad, wind_speed, wind_dir,
                vav1_damper_pos, vav1_damper_pos_min,
                chiller_electricity, chiller_evaporator_outlet_temp,
                chiller_evaporator_outlet_temp_high, chiller_evaporator_outlet_temp_low,
                chiller_evaporator_mass_flow_rate, chillerEvaporatorOutletTempAct,
                chillerEvaporatorOutletTempActMin, chillerEvaporatorOutletTempActMax,
                vav1MdotKgSAct]
    if any([x < 0 for x in _allHandles]):
        raise Exception("Error: Invalid handle")

    zone_temp_c = get_zone_handles(state)

    allHandles['sensor']['OAT_C'] = oat_c
    allHandles['sensor']['Direct_Solar_Radiation'] = direct_rad
    allHandles['sensor']['Diffuse_Solar_Radiation'] = diffuse_rad
    allHandles['sensor']['Wind_Speed'] = wind_speed
    allHandles['sensor']['Wind_Direction'] = wind_dir
    allHandles['sensor']['VAV1_Damper_Position'] = vav1_damper_pos
    allHandles['sensor']['VAV1_Damper_Position_Min'] = vav1_damper_pos_min
    allHandles['sensor']['Chiller_Electricity'] = chiller_electricity
    allHandles['sensor']['Chiller_Evaporator_Outlet_Temperature'] = chiller_evaporator_outlet_temp
    allHandles['sensor']['Chiller_Evaporator_Outlet_Temperature_High'] = chiller_evaporator_outlet_temp_high
    allHandles['sensor']['Chiller_Evaporator_Outlet_Temperature_Low'] = chiller_evaporator_outlet_temp_low
    allHandles['sensor']['Chiller_Evaporator_Mass_Flow_Rate'] = chiller_evaporator_mass_flow_rate
    allHandles['sensor']['room_temp_c'] = zone_temp_c
    allHandles['actuator']['ChillerEvaporatorOutletTempAct'] = chillerEvaporatorOutletTempAct
    allHandles['actuator']['ChillerEvaporatorOutletTempActMin'] = chillerEvaporatorOutletTempActMin
    allHandles['actuator']['ChillerEvaporatorOutletTempActMax'] = chillerEvaporatorOutletTempActMax
    allHandles['actuator']['VAV1MdotKgSAct'] = vav1MdotKgSAct
def get_sensor_value(state):
    sensor_values = {}
    dayofMonth = ep_api.exchange.day_of_month(state)
    dayofWk = ep_api.exchange.day_of_week(state)
    hourOfDay = ep_api.exchange.hour(state)
    sensor_values['dayofMonth'] = dayofMonth
    sensor_values['dayofWk'] = dayofWk
    sensor_values['hourOfDay'] = hourOfDay

    time_in_hours = ep_api.exchange.current_sim_time(state)
    _readable_time = datetime.timedelta(hours=time_in_hours)
    print('Time: ', _readable_time)

    sensor_values['OAT_C'] = ep_api.exchange.get_variable_value(state, allHandles['sensor']['OAT_C'])
    sensor_values['Direct_Solar_Radiation'] = ep_api.exchange.get_variable_value(state,
                                                                                 allHandles['sensor']['Direct_Solar_Radiation'])
    sensor_values['Diffuse_Solar_Radiation'] = ep_api.exchange.get_variable_value(state,
                                                                                        allHandles['sensor']['Diffuse_Solar_Radiation'])
    sensor_values['Wind_Speed'] = ep_api.exchange.get_variable_value(state, allHandles['sensor']['Wind_Speed'])
    sensor_values['Wind_Direction'] = ep_api.exchange.get_variable_value(state,
                                                                           allHandles['sensor']['Wind_Direction'])
    sensor_values['VAV1_Damper_Position'] = ep_api.exchange.get_variable_value(state,
                                                                                    allHandles['sensor']['VAV1_Damper_Position'])
    sensor_values['VAV1_Damper_Position_Min'] = ep_api.exchange.get_variable_value(state,
                                                                                        allHandles['sensor']['VAV1_Damper_Position_Min'])
    sensor_values['Chiller_Electricity'] = ep_api.exchange.get_variable_value(state,
                                                                                 allHandles['sensor']['Chiller_Electricity'])
    sensor_values['Chiller_Evaporator_Outlet_Temperature'] = ep_api.exchange.get_variable_value(state,
                                                                                 allHandles['sensor']['Chiller_Evaporator_Outlet_Temperature'])
    sensor_values['Chiller_Evaporator_Outlet_Temperature_High'] = ep_api.exchange.get_variable_value(state,
                                                                                    allHandles['sensor']['Chiller_Evaporator_Outlet_Temperature_High'])
    sensor_values['Chiller_Evaporator_Outlet_Temperature_Low'] = ep_api.exchange.get_variable_value(state,
                                                                                    allHandles['sensor']['Chiller_Evaporator_Outlet_Temperature_Low'])
    sensor_values['Chiller_Evaporator_Mass_Flow_Rate'] = ep_api.exchange.get_variable_value(state,
                                                                                 allHandles['sensor']['Chiller_Evaporator_Mass_Flow_Rate'])
    sensor_values['room_temp_c'] = []
    for i in range(len(allHandles['sensor']['room_temp_c'])):
        sensor_values['room_temp_c'].append(
            ep_api.exchange.get_variable_value(state, allHandles['sensor']['room_temp_c'][i]))
    return sensor_values

def set_actuators(state):
    # '_chillerEvaOutTempCVal: range 4 to 15'
    # _chillerSWTMinCVal = -999
    # _chillerSWTMaxCVal = -999

    _chillerEvaOutTempCVal = 14
    ep_api.exchange.set_actuator_value(state,
       allHandles['actuator']['ChillerEvaporatorOutletTempAct'],_chillerEvaOutTempCVal)

    airRhoKgM3 = 1.293
    vav1MdotM3SMax = 0.221001
    _vav1TargetFraction = 0.7
    _temVAV1KgSVal = vav1MdotM3SMax * airRhoKgM3 * _vav1TargetFraction
    # ep_api.exchange.set_actuator_value(state,
    #     allHandles['actuator']['VAV1MdotKgSAct'], _temVAV1KgSVal)

    # ep_api.exchange.set_actuator_value(state,
    #      allHandles['actuator']['ChillerEvaporatorOutletTempActMin'],_chillerSWTMinCVal)
    # ep_api.exchange.set_actuator_value(state,
    #         allHandles['actuator']['ChillerEvaporatorOutletTempActMax'],_chillerSWTMaxCVal)

def api_to_csv(state):
    orig = ep_api.exchange.list_available_api_data_csv(state)
    newFileByteArray = bytearray(orig)
    api_path = os.path.join(os.path.dirname(__file__), 'api_data.csv')
    newFile = open(api_path, "wb")
    newFile.write(newFileByteArray)
    newFile.close()
def timeStepHandlerToObsere(state):
    if not ep_api.exchange.api_data_fully_ready(state):
        return
    global get_handle_bool
    if not get_handle_bool:
        get_building_handles(state)
        get_handle_bool = True
        # api_to_csv(state)
    warm_up = ep_api.exchange.warmup_flag(state)
    if not warm_up:
        sensor_values = get_sensor_value(state)
        global safeToOverwrite
        if not safeToOverwrite:
            safeToOverwrite = True
        line = ""
        for _k in sensor_values.keys():
            if "Chiller" in _k or "VAV" in _k:
                line += f"{_k} : {sensor_values[_k]}  "
        print(line)

def timeStepHandlerToOverwrite(state):
    if safeToOverwrite:
        set_actuators(state)
def init():
    global ep_api, get_handle_bool, safeToOverwrite
    get_handle_bool = False
    safeToOverwrite = False
    ep_api = EnergyPlusAPI()
    state = ep_api.state_manager.new_state()
    '''
    callback_begin_system_timestep_before_predictor
        reduce lighting or process loads, change thermostat settings,
    callback_after_predictor_before_hvac_managers
        the EMS control actions could be overwritten by other SetpointManager
    ✅callback_after_predictor_after_hvac_managers
        SetpointManager or AvailabilityManager actions may be overwritten by EMS control actions.
    ..before reporting
        custom output
    callback_end_system_timestep_after_hvac_reporting
    callback_end_zone_timestep_after_zone_reporting
    '''
    ep_api.runtime.callback_after_predictor_after_hvac_managers(state, timeStepHandlerToOverwrite)
    ep_api.runtime.callback_end_zone_timestep_after_zone_reporting(state, timeStepHandlerToObsere)

    ep_api.exchange.request_variable(state, "Site Outdoor Air Drybulb Temperature", "ENVIRONMENT")
    ep_api.exchange.request_variable(state, "Site Direct Solar Radiation Rate per Area", "ENVIRONMENT")
    ep_api.exchange.request_variable(state, "Site Diffuse Solar Radiation Rate per Area", "ENVIRONMENT")
    ep_api.exchange.request_variable(state, "Site Wind Speed", "ENVIRONMENT")
    ep_api.exchange.request_variable(state, "Site Wind Direction", "ENVIRONMENT")
    '''
    OutputVariable,Chiller Evaporator Inlet Temperature,CENTRAL CHILLER,[C]
    OutputVariable,Chiller Evaporator Outlet Temperature,CENTRAL CHILLER,[C]
    OutputVariable,Chiller Evaporator Mass Flow Rate,CENTRAL CHILLER,[kg/s]
    Zone Air Terminal VAV Damper Position, SPACE1-1 VAV Reheat
    Zone Air Terminal Minimum Air Flow Fraction, SPACE1-1 VAV Reheat
    '''
    ep_api.exchange.request_variable(state, "Chiller Evaporator Outlet Temperature", "CENTRAL CHILLER")
    ep_api.exchange.request_variable(state, "System Node Setpoint High Temperature", "CENTRAL CHILLER OUTLET NODE")
    ep_api.exchange.request_variable(state, "System Node Setpoint Low Temperature", "CENTRAL CHILLER OUTLET NODE")
    ep_api.exchange.request_variable(state, "Chiller Evaporator Mass Flow Rate", "CENTRAL CHILLER")
    ep_api.exchange.request_variable(state, "Zone Air Terminal VAV Damper Position", "SPACE1-1 VAV Reheat")
    ep_api.exchange.request_variable(state, "Zone Air Terminal Minimum Air Flow Fraction", "SPACE1-1 VAV Reheat")

    return state
def main(idfFilePath, weather_file_path):
    state = init()
    output_path = './ep_trivial'
    sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
    ep_api.runtime.run_energyplus(state, sys_args)
    ep_api.state_manager.reset_state(state)

if __name__ == '__main__':
    _idf = '5ZoneAirCooled_VAVBoxMinAirFlowTurnDown.idf'
    _epw = 'USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw'
    _idfPath = os.path.join('0resources',_idf)
    _epwPath = os.path.join('0resources',_epw)
    main(_idfPath, _epwPath)