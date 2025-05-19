import os, sys
sys.path.insert(0, '/usr/local/EnergyPlus-24-2-0/')
sys.path.insert(0, 'C:/EnergyPlusV24-2-0')
from pyenergyplus.api import EnergyPlusAPI
def api_to_csv(state):
    orig = ep_api.exchange.list_available_api_data_csv(state)
    newFileByteArray = bytearray(orig)
    api_path = os.path.join(os.path.dirname(__file__), 'api_data.csv')
    newFile = open(api_path, "wb")
    newFile.write(newFileByteArray)
    newFile.close()
def timeStepHandler(state):
    global get_handle_bool
    if not get_handle_bool:
        get_handle_bool = True
        api_to_csv(state)
    warm_up = ep_api.exchange.warmup_flag(state)
    if not warm_up:
        pass
def init():
    global ep_api, get_handle_bool
    get_handle_bool = False
    ep_api = EnergyPlusAPI()
    state = ep_api.state_manager.new_state()
    ep_api.runtime.callback_after_predictor_before_hvac_managers(state, timeStepHandler)
    return state
def main(idfFilePath, weather_file_path):
    state = init()
    output_path = './ep_trivial'
    sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
    ep_api.runtime.run_energyplus(state, sys_args)

if __name__ == '__main__':
    _idf = '5ZoneAirCooled_VAVBoxMinAirFlowTurnDown.idf'
    _epw = 'USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw'
    _idfPath = os.path.join('0resources',_idf)
    _epwPath = os.path.join('0resources',_epw)
    main(_idfPath, _epwPath)