""" fauxmo_minimal.py - Fabricate.IO

    This is a demo python file showing what can be done with the debounce_handler.
    The handler prints True when you say "Alexa, device on" and False when you say
    "Alexa, device off".

    If you have two or more Echos, it only handles the one that hears you more clearly.
    You can have an Echo per room and not worry about your handlers triggering for
    those other rooms.

    The IP of the triggering Echo is also passed into the act() function, so you can
    do different things based on which Echo triggered the handler.
"""

import fauxmo
import logging
import time
import RPi.GPIO as GPIO

#from debounce_handler import debounce_handler
from pi_switch import RCSwitchSender
from lirc import Lirc

# Define variable
# Common
HIGH    = True
LOW     = False

# For TV
TV_MANUFACTORE  = 'Samsung'

# For Speaker
SPEAKER_OUT         = 21
SPEAKER_HOLD_TIME   = 3

# For Light
TABLE_LAMP_OFF_COMMAND         = 0x00EC083B
TABLE_LAMP_ON_COMMAND          = 0x00EC083C
LIVINGROOM_LAMP_OFF_COMMAND    = 0x00EB083D
LIVINGROOM_LAMP_ON_COMMAND     = 0x00EB083C
WINDOW_LAMP_OFF_COMMAND        = 0x00EA083E
WINDOW_LAMP_ON_COMMAND         = 0x00EA083F


# Setup logging level
logging.basicConfig(level=logging.ERROR)

# Lirc Init
lirc_obj = Lirc()

# RF Switch Init
rf_sender = RCSwitchSender()
rf_sender.enableTransmit(0) # GPIO_GEN_0

# GPIO Init
GPIO.setmode(GPIO.BCM)
GPIO.setup(SPEAKER_OUT, GPIO.OUT)
GPIO.output(SPEAKER_OUT, HIGH)


# RCU Operation
def RCU_Operation(key_code):
    logging.debug("RCU : code %s", key_code)
    lirc_obj.send_once(TV_MANUFACTORE, key_code)

# RF Operation
def RF_Operation(key_code):
    logging.debug("RF : code %s", key_code)
    rf_sender.sendDecimal(key_code, 24)

# GPIO Operation
def GPIO_Operation(key_code):
    logging.debug("GPIO : code %s", key_code)
    GPIO.output(key_code, LOW)
    time.sleep(SPEAKER_HOLD_TIME)
    GPIO.output(key_code, HIGH)


# [0] : Device Name
# [1] : Port Number
# [2] : Function
# [3] : On key
# [4] : Off key
# [5] : On/Off Status
FAUXMO_DEVICES = [
    ["TV", 52000, RCU_Operation, 'KEY_POWER', 'KEY_POWER', 2],
    ["Speaker", 52001, GPIO_Operation, SPEAKER_OUT, SPEAKER_OUT, 2],
    ["Table", 52002, RF_Operation, TABLE_LAMP_ON_COMMAND, TABLE_LAMP_OFF_COMMAND, 2],
    ["Center", 52003, RF_Operation, LIVINGROOM_LAMP_ON_COMMAND, LIVINGROOM_LAMP_OFF_COMMAND, 2],
    ["Window", 52004, RF_Operation, WINDOW_LAMP_ON_COMMAND, WINDOW_LAMP_OFF_COMMAND, 2],
    ["Trick", 52005, RCU_Operation, 'KEY_PLAYPAUSE', 'KEY_PLAYPAUSE', 2],
    ["Volume", 52006, RCU_Operation, 'KEY_VOLUMEUP', 'KEY_VOLUMEDOWN', 2],
    ["Stop", 52007, RCU_Operation, 'KEY_STOP', 'KEY_STOP', 2],
]

# Main Function
class device_handler(object):
    """Publishes the on/off state requested,
       and the IP address of the Echo making the request.
    """
    def __init__(self, name):
        self.name = name

    def on(self, client_address, name):
        logging.debug("%s from %s on", name, client_address)
        for one_faux in FAUXMO_DEVICES:
            if one_faux[0] == name:
                one_faux[2](one_faux[3])
                one_faux[5] = 1
        return True

    def off(self, client_address, name):
        logging.debug("%s from %s off", name, client_address)
        for one_faux in FAUXMO_DEVICES:
            if one_faux[0] == name:
                one_faux[2](one_faux[4])
                one_faux[5] = 0
        return True

    def get(self, client_address, name):
        on_off_status = 2
        #for one_faux in FAUXMO_DEVICES:
        #    if one_faux[0] == name:
        #        on_off_status = one_faux[5]
        return on_off_status


if __name__ == "__main__":
    # Startup the fauxmo server
    fauxmo.DEBUG = False
    p = fauxmo.poller()
    u = fauxmo.upnp_broadcast_responder()
    u.init_socket()
    p.add(u)

    # Register the device callback as a fauxmo handler
    for one_faux in FAUXMO_DEVICES:
        fauxmo.fauxmo(one_faux[0], u, p, None, one_faux[1], action_handler = device_handler(""))

    # Loop and poll for incoming Echo requests
    logging.debug("Entering fauxmo polling loop")
    while True:
        try:
            # Allow time for a ctrl-c to stop the process
            p.poll(100)
            time.sleep(0.1)
        except Exception, e:
            logging.critical("Critical exception: " + str(e))
            break

# Exit script
GPIO.cleanup()
