import time
from flask import Flask, request
from pi_switch import RCSwitchSender
from lirc import Lirc

import logging


# For TV
TV_MANUFACTORE  = 'Samsung'

# For Light
TABLE_LAMP_OFF_COMMAND         = 0x00EC083B
TABLE_LAMP_ON_COMMAND          = 0x00EC083C
LIVINGROOM_LAMP_OFF_COMMAND    = 0x00EB083D
LIVINGROOM_LAMP_ON_COMMAND     = 0x00EB083C
WINDOW_LAMP_OFF_COMMAND        = 0x00EA083E
WINDOW_LAMP_ON_COMMAND         = 0x00EA083F
GROUP_ON_COMMAND               = 0xABCDEF00
GROUP_OFF_COMMAND              = 0xABCDEF11


# Lirc Init
lirc_obj = Lirc()

# RF Switch Init
rf_sender = RCSwitchSender()
rf_sender.enableTransmit(0) # GPIO_GEN_0

# Flash Init
app = Flask(__name__)

# Setup logging level
logging.basicConfig(level=logging.DEBUG)


# RCU Operation
def RCU_Operation(key_code):
    logging.debug("RCU : code %s", key_code)
    lirc_obj.send_once(TV_MANUFACTORE, key_code)

# RF Operation
def RF_Operation(key_code):
    logging.debug("RF : code %s", key_code)
    rf_sender.sendDecimal(key_code, 24)



# [0] : Device Name
# [1] : Function
# [2] : On key
# [3] : Off key
# [4] : group
DEVICE_LIST = [
    ["TV", RCU_Operation, 'KEY_POWER', 'KEY_POWER', 0],
    ["table", RF_Operation, TABLE_LAMP_ON_COMMAND, TABLE_LAMP_OFF_COMMAND, 1],
    ["center", RF_Operation, LIVINGROOM_LAMP_ON_COMMAND, LIVINGROOM_LAMP_OFF_COMMAND, 1],
    ["window", RF_Operation, WINDOW_LAMP_ON_COMMAND, WINDOW_LAMP_OFF_COMMAND, 1],
    ["living room", RF_Operation, GROUP_ON_COMMAND, GROUP_OFF_COMMAND, 0],
]

# [0] : Command Name
# [1] : Function
# [2] : key
TV_COMMAND_LIST = [
    ["pause", RCU_Operation, 'KEY_PLAYPAUSE'],
    ["play", RCU_Operation, 'KEY_PLAYPAUSE'],
    ["stop", RCU_Operation, 'KEY_STOP'],
    ["volume up", RCU_Operation, 'KEY_VOLUMEUP'],
    ["volume down", RCU_Operation, 'KEY_VOLUMEDOWN'],
]



@app.route('/')
def index():
    return 'OK'

@app.route('/homeauto')
def index_sub():
    return 'OK'

@app.route('/homeauto/power_on', methods=['GET','POST'])
def power_on():
    contents=request.args.get('device')
    device_name=contents.replace("the ", "").strip()
    logging.debug("Power on device is %s", device_name)
    for one_device in DEVICE_LIST:
        if one_device[0] == device_name:
            if one_device[2] == GROUP_ON_COMMAND:
                # Do on poeration for groupped debice
                for sub_device in DEVICE_LIST:
                    if sub_device[4] == 1:
                        sub_device[1](sub_device[2])
                        time.sleep(0.5)
            else:
                one_device[1](one_device[2])
    return "OK"

@app.route('/homeauto/power_off', methods=['GET','POST'])
def power_off():
    contents=request.args.get('device')
    device_name=contents.replace("the ", "").strip()    
    logging.debug("Power off device is %s", device_name)
    for one_device in DEVICE_LIST:
        if one_device[0] == device_name:
            if one_device[3] == GROUP_OFF_COMMAND:
                # Do off poeration for groupped debice
                for sub_device in DEVICE_LIST:
                    if sub_device[4] == 1:
                        sub_device[1](sub_device[3])
                        time.sleep(0.5)
            else:
                one_device[1](one_device[3])
    return "OK"

@app.route('/homeauto/tv', methods=['GET','POST'])
def tv_control():
    command_name=request.args.get('command')
    logging.debug("TV command is %s", command_name)
    for command in TV_COMMAND_LIST:
        if command[0] == command_name:
            command[1](command[2])
    return "OK"



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4002, debug=False)
