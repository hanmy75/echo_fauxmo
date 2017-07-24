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

from debounce_handler import debounce_handler
from pi_switch import RCSwitchSender
from lirc import Lirc

# Define variable
# Common
HIGH    = True
LOW     = False

# For TV
TV_MANUFACTORE  = 'Samsung'
TV_COMMAND      = 'KEY_POWER'

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


# Operation
def TV_Operation(state):
    lirc_obj.send_once(TV_MANUFACTORE, TV_COMMAND)

def Speaker_Operation(state):
    GPIO.output(SPEAKER_OUT, LOW)
    time.sleep(SPEAKER_HOLD_TIME)
    GPIO.output(SPEAKER_OUT, HIGH)

def TableLamp_Operation(state):
    if state:
        rf_sender.sendDecimal(TABLE_LAMP_ON_COMMAND, 24)
    else:
        rf_sender.sendDecimal(TABLE_LAMP_OFF_COMMAND, 24)
    time.sleep(0.5)

def LivingRoom_Operation(state):
    if state:
        rf_sender.sendDecimal(LIVINGROOM_LAMP_ON_COMMAND, 24)
    else:
        rf_sender.sendDecimal(LIVINGROOM_LAMP_OFF_COMMAND, 24)
    time.sleep(0.5)

def WindowLamp_Operation(state):
    if state:
        rf_sender.sendDecimal(WINDOW_LAMP_ON_COMMAND, 24)
    else:
        rf_sender.sendDecimal(WINDOW_LAMP_OFF_COMMAND, 24)
    time.sleep(0.5)


# Main Function
class device_handler(debounce_handler):
    """Publishes the on/off state requested,
       and the IP address of the Echo making the request.
    """
    TRIGGERS = {
        "TV":           52000,
        "Speaker":     	52001,
        "Table":   	52002,
        "Center":  	52003,
        "Window":  	52004,                                              
    }

    OPERATIONS = {
        "TV":           TV_Operation,
        "Speaker":     	Speaker_Operation,
        "Table":   	TableLamp_Operation,
        "Center":  	LivingRoom_Operation,
        "Window":  	WindowLamp_Operation,   
    }

    def act(self, client_address, state, name):
        print "State", state, "on ", name, "from client @", client_address
        func = self.OPERATIONS[name]
        func(state)
        return True

if __name__ == "__main__":
    # Startup the fauxmo server
    fauxmo.DEBUG = False
    p = fauxmo.poller()
    u = fauxmo.upnp_broadcast_responder()
    u.init_socket()
    p.add(u)

    # Register the device callback as a fauxmo handler
    d = device_handler()
    for trig, port in d.TRIGGERS.items():
        fauxmo.fauxmo(trig, u, p, None, port, d)

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
