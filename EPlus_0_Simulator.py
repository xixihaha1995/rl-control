import sys, threading,datetime
sys.path.insert(0, 'C:/EnergyPlusV24-1-0')
from pyenergyplus.api import EnergyPlusAPI
class EPlusSimulatorForGymEnv(object):
    def __int__(self, obsQ, actQ):
        self.ep_api = EnergyPlusAPI()
        self.obs_queue = obsQ
        self.act_queue = actQ
        self.safeToOverwrite = False

    def start(self):
        _idf = '5ZoneAirCooled_VAVBoxMinAirFlowTurnDown.idf'
        _epw = 'USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw'
        self.ep_api.state_manager.reset_state(self.state)
        self.state = self.ep_api.state_manager.new_state()

        self.ep_api.runtime.callback_after_predictor_after_hvac_managers(self.state, self.timeStepHandlerToOverwrite)
        self.ep_api.runtime.callback_end_zone_timestep_after_zone_reporting(self.state, self.timeStepHandlerToObsere)
        #obs
        self.ep_api.exchange.request_variable(self.state, "Site Outdoor Air Drybulb Temperature", "ENVIRONMENT")
        self.ep_api.exchange.request_variable(self.state, "Site Direct Solar Radiation Rate per Area", "ENVIRONMENT")
        self.ep_api.exchange.request_variable(self.state, "Site Diffuse Solar Radiation Rate per Area", "ENVIRONMENT")
        self.ep_api.exchange.request_variable(self.state, "Site Wind Speed", "ENVIRONMENT")
        self.ep_api.exchange.request_variable(self.state, "Site Wind Direction", "ENVIRONMENT")

        #not necessarilly useful
        self.ep_api.exchange.request_variable(self.state, "Chiller Evaporator Outlet Temperature", "CENTRAL CHILLER")
        self.ep_api.exchange.request_variable(self.state, "System Node Setpoint High Temperature", "CENTRAL CHILLER OUTLET NODE")
        self.ep_api.exchange.request_variable(self.state, "System Node Setpoint Low Temperature", "CENTRAL CHILLER OUTLET NODE")
        self.ep_api.exchange.request_variable(self.state, "Chiller Evaporator Mass Flow Rate", "CENTRAL CHILLER")
        self.ep_api.exchange.request_variable(self.state, "Zone Air Terminal VAV Damper Position", "SPACE1-1 VAV Reheat")
        self.ep_api.exchange.request_variable(self.state, "Zone Air Terminal Minimum Air Flow Fraction", "SPACE1-1 VAV Reheat")

        output_path = './ep_trivial'
        sys_args = '-d', output_path, '-w', _epw, _idf
        def _run_energyplus(_sys_args):
            self.ep_api.runtime.run_energyplus(self.state, _sys_args)
            self.simulation_complete = True
        self.energyplus_thread = threading.Thread(
            target=_run_energyplus,
            args=(sys_args),
            daemon=True
        )
        self.energyplus_thread.start()

    def stop(self):
        if self.energyplus_thread is None:
            return
        self.simulation_complete = True
        # Unblock action thread if needed
        if self.act_queue.empty():
            self.act_queue.put([0] * len(self.actuators))
        # Wait to thread to finish (without control)
        self.energyplus_thread.join()
        self._flush_queues()
        # Delete thread
        self.energyplus_thread = None
        # Clean runtime callbacks
        self.ep_api.runtime.clear_callbacks()
        # Clean Energyplus state
        self.ep_api.state_manager.delete_state(
            self.state)
        self.simulation_complete = False

    def _flush_queues(self) -> None:
        """It empties all values allocated in observation, action and warmup queues
        """
        for q in [self.obs_queue,self.act_queue]:
            while not q.empty():
                q.get()
    def timeStepHandlerToOverwrite(self, state):
        if not self.safeToOverwrite:
            return
        next_action = self.act_queue.get()

        _chillerEvaOutTempCVal = 14
        self.ep_api.exchange.set_actuator_value(state,
                                           allHandles['actuator']['ChillerEvaporatorOutletTempAct'],
                                           _chillerEvaOutTempCVal)
        airRhoKgM3 = 1.293
        vav1MdotM3SMax = 0.221001
        _vav1TargetFraction = 0.7
        _temVAV1KgSVal = vav1MdotM3SMax * airRhoKgM3 * _vav1TargetFraction

    def timeStepHandlerToObsere(self, state):
        if not self.ep_api.exchange.api_data_fully_ready(state):
            return
        global get_handle_bool
        if not get_handle_bool:
            self.get_building_handles(state)
            get_handle_bool = True
            # api_to_csv(state)
        warm_up = self.ep_api.exchange.warmup_flag(state)
        if not warm_up:
            sensor_values = self.get_sensor_value(state)
            global safeToOverwrite
            if not safeToOverwrite:
                safeToOverwrite = True
            line = ""
            for _k in sensor_values.keys():
                if "Chiller" in _k or "VAV" in _k:
                    line += f"{_k} : {sensor_values[_k]}  "
            print(line)

    def get_building_handles(self, state):
        global allHandles
        allHandles = {}
        allHandles['sensor'] = {}
        allHandles['actuator'] = {}
        oat_c = self.ep_api.exchange.get_variable_handle(state,"Site Outdoor Air Drybulb Temperature",
                                                                                 "Environment")
        direct_rad = self.ep_api.exchange.get_variable_handle(state,"Site Direct Solar Radiation Rate per Area",
                                                                                    "Environment")
        diffuse_rad = self.ep_api.exchange.get_variable_handle(state,"Site Diffuse Solar Radiation Rate per Area",
                                                                                    "Environment")
        wind_speed = self.ep_api.exchange.get_variable_handle(state,"Site Wind Speed","Environment")
        wind_dir = self.ep_api.exchange.get_variable_handle(state,"Site Wind Direction","Environment")
        #OutputVariable,Chiller Electricity Energy,CENTRAL CHILLER,[J]
        # self.ep_api.exchange.request_variable(state, "Chiller Evaporator Outlet Temperature", "CENTRAL CHILLER")
        # self.ep_api.exchange.request_variable(state, "Chiller Evaporator Mass Flow Rate", "CENTRAL CHILLER")

        vav1_damper_pos = self.ep_api.exchange.get_variable_handle(state,
                                                            "Zone Air Terminal VAV Damper Position",
                                                            "SPACE1-1 VAV Reheat")
        vav1_damper_pos_min = self.ep_api.exchange.get_variable_handle(state,
                                                            "Zone Air Terminal Minimum Air Flow Fraction",
                                                            "SPACE1-1 VAV Reheat")

        chiller_electricity = self.ep_api.exchange.get_variable_handle(state,"Chiller Electricity Energy",
                                                                        "CENTRAL CHILLER")
        chiller_evaporator_outlet_temp = self.ep_api.exchange.get_variable_handle(state,
                                                                        "Chiller Evaporator Outlet Temperature",
                                                                        "CENTRAL CHILLER")
        chiller_evaporator_outlet_temp_high = self.ep_api.exchange.get_variable_handle(state,
                                                                        "System Node Setpoint High Temperature",
                                                                        "CENTRAL CHILLER OUTLET NODE")
        chiller_evaporator_outlet_temp_low = self.ep_api.exchange.get_variable_handle(state,
                                                                        "System Node Setpoint Low Temperature",
                                                                        "CENTRAL CHILLER OUTLET NODE")
        chiller_evaporator_mass_flow_rate = self.ep_api.exchange.get_variable_handle(state,
                                                                        "Chiller Evaporator Mass Flow Rate",
                                                                        "CENTRAL CHILLER")
        '''
        Actuator,System Node Setpoint,Temperature Setpoint,CENTRAL CHILLER OUTLET NODE,[C]
        Actuator,System Node Setpoint,Temperature Minimum Setpoint,CENTRAL CHILLER OUTLET NODE,[C]
        Actuator,System Node Setpoint,Temperature Maximum Setpoint,CENTRAL CHILLER OUTLET NODE,[C]
        Actuator,System Node Setpoint,Mass Flow Rate Setpoint,SPACE1-1 NODE,[kg/s]
        '''
        chillerEvaporatorOutletTempAct = self.ep_api.exchange.get_actuator_handle(state,
                                                                        "System Node Setpoint",
                                                                        "Temperature Setpoint",
                                                                        "CENTRAL CHILLER OUTLET NODE")
        chillerEvaporatorOutletTempActMin = self.ep_api.exchange.get_actuator_handle(state,
                                                                        "System Node Setpoint",
                                                                        "Temperature Minimum Setpoint",
                                                                        "CENTRAL CHILLER OUTLET NODE")
        chillerEvaporatorOutletTempActMax = self.ep_api.exchange.get_actuator_handle(state,
                                                                        "System Node Setpoint",
                                                                        "Temperature Maximum Setpoint",
                                                                        "CENTRAL CHILLER OUTLET NODE")
        vav1MdotKgSAct = self.ep_api.exchange.get_actuator_handle(state,
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

        zone_temp_c = self.get_zone_handles(state)

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

    def get_zone_handles(self,state):
        global zone_names
        zone_names = ['SPACE1-1',
                      'SPACE2-1',
                      'SPACE3-1',
                      'SPACE4-1',
                      'SPACE5-1']
        zone_temp_c = []
        for zone in zone_names:
            _tmpRtemp = self.ep_api.exchange.get_variable_handle(state,
                                                       "Zone Air Temperature",
                                                       zone)
            if _tmpRtemp < 0:
                raise Exception("Error: Invalid handle for zone: "+zone)
            zone_temp_c.append(_tmpRtemp)

        return zone_temp_c

    def get_sensor_value(self,state):
        sensor_values = {}
        dayofMonth = self.ep_api.exchange.day_of_month(state)
        dayofWk = self.ep_api.exchange.day_of_week(state)
        hourOfDay = self.ep_api.exchange.hour(state)
        sensor_values['dayofMonth'] = dayofMonth
        sensor_values['dayofWk'] = dayofWk
        sensor_values['hourOfDay'] = hourOfDay

        time_in_hours = self.ep_api.exchange.current_sim_time(state)
        _readable_time = datetime.timedelta(hours=time_in_hours)
        print('Time: ', _readable_time)

        sensor_values['OAT_C'] = self.ep_api.exchange.get_variable_value(state, allHandles['sensor']['OAT_C'])
        sensor_values['Direct_Solar_Radiation'] = self.ep_api.exchange.get_variable_value(state,
                                                                                     allHandles['sensor'][
                                                                                         'Direct_Solar_Radiation'])
        sensor_values['Diffuse_Solar_Radiation'] = self.ep_api.exchange.get_variable_value(state,
                                                                                      allHandles['sensor'][
                                                                                          'Diffuse_Solar_Radiation'])
        sensor_values['Wind_Speed'] = self.ep_api.exchange.get_variable_value(state, allHandles['sensor']['Wind_Speed'])
        sensor_values['Wind_Direction'] = self.ep_api.exchange.get_variable_value(state,
                                                                             allHandles['sensor']['Wind_Direction'])
        sensor_values['VAV1_Damper_Position'] = self.ep_api.exchange.get_variable_value(state,
                                                                                   allHandles['sensor'][
                                                                                       'VAV1_Damper_Position'])
        sensor_values['VAV1_Damper_Position_Min'] = self.ep_api.exchange.get_variable_value(state,
                                                                                       allHandles['sensor'][
                                                                                           'VAV1_Damper_Position_Min'])
        sensor_values['Chiller_Electricity'] = self.ep_api.exchange.get_variable_value(state,
                                                                                  allHandles['sensor'][
                                                                                      'Chiller_Electricity'])
        sensor_values['Chiller_Evaporator_Outlet_Temperature'] = self.ep_api.exchange.get_variable_value(state,
                                                                                                    allHandles[
                                                                                                        'sensor'][
                                                                                                        'Chiller_Evaporator_Outlet_Temperature'])
        sensor_values['Chiller_Evaporator_Outlet_Temperature_High'] = self.ep_api.exchange.get_variable_value(state,
                                                                                                         allHandles[
                                                                                                             'sensor'][
                                                                                                             'Chiller_Evaporator_Outlet_Temperature_High'])
        sensor_values['Chiller_Evaporator_Outlet_Temperature_Low'] = self.ep_api.exchange.get_variable_value(state,
                                                                                                        allHandles[
                                                                                                            'sensor'][
                                                                                                            'Chiller_Evaporator_Outlet_Temperature_Low'])
        sensor_values['Chiller_Evaporator_Mass_Flow_Rate'] = self.ep_api.exchange.get_variable_value(state,
                                                                                                allHandles['sensor'][
                                                                                                    'Chiller_Evaporator_Mass_Flow_Rate'])
        sensor_values['room_temp_c'] = []
        for i in range(len(allHandles['sensor']['room_temp_c'])):
            sensor_values['room_temp_c'].append(
                self.ep_api.exchange.get_variable_value(state, allHandles['sensor']['room_temp_c'][i]))

        self.next_obs = {
            # time variables (calling in exchange module directly)
            **{
                t_variable: eval('self.exchange.' +
                                 t_variable +
                                 '(self.energyplus_state)', {'self': self})
                for t_variable in self.time_variables
            },
            # variables (getting value from handlers)
            ** {
                key: self.exchange.get_variable_value(state_argument, handle)
                for key, handle
                in self.var_handlers.items()
            },
            # meters (getting value from handlers)
            **{
                key: self.exchange.get_meter_value(state_argument, handle)
                for key, handle
                in self.meter_handlers.items()
            }
        }
        self.obs_queue.put(self.next_obs)
        return sensor_values
