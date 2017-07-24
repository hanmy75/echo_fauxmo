from OpenSSL import SSL
from flask import Flask
from flask_ask import Ask, statement, convert_errors
from lirc import Lirc

import logging


# For TV
TV_MANUFACTORE  = 'Samsung'

# Lirc Init
lirc_obj = Lirc()

# Flash Init
app = Flask(__name__)
ask = Ask(app, '/kodi')

# Set Log level
logging.getLogger("flask_ask").setLevel(logging.ERROR)


@ask.intent('AMAZON.PauseIntent')
def PauseFunction():
    lirc_obj.send_once(TV_MANUFACTORE, 'KEY_PLAYPAUSE')
    return statement('OK')

@ask.intent('AMAZON.ResumeIntent')
def ResumeFunction():
    lirc_obj.send_once(TV_MANUFACTORE, 'KEY_PLAYPAUSE')
    return statement('OK')

@ask.intent('AMAZON.StopIntent')
def StopFunction():
    lirc_obj.send_once(TV_MANUFACTORE, 'KEY_STOP')
    return statement('OK')

@ask.intent('VolumeIntent', mapping={'volume': 'volume'})
def VolumeFunction(volume):
    if volume in ['up']:    lirc_obj.send_once(TV_MANUFACTORE, 'KEY_VOLUMEUP')
    if volume in ['down']:  lirc_obj.send_once(TV_MANUFACTORE, 'KEY_VOLUMEDOWN')
    return statement('OK')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4001, debug=False)
