#!/usr/bin/env python
#
# Raspberry Pi REST API for relay module boards.
# Easy adaptable to 1,2,4,8 relay modules.
# Intended use: multi purpose remote switch
# - automatically switch on/off laser printers with Tea4CUPS prehooks & posthooks
# - NEEO power switch device 
#
# Tested with: 
# - Python 2.7.9
# - Bottle 0.12     http://bottlepy.org/
# - gpiozero 1.4.0  https://gpiozero.readthedocs.io
# - Raspberry Pi 2 running Raspbian Jessie
# - Noname "Arduino 4 channel relay module board" from eBay
#
from bottle import route, get, put, request, HTTPResponse, run
from gpiozero import OutputDevice

import argparse
import time
import logging
import logging.handlers
import sys

# constants
# BCM numbers where the relays are connected. See: https://pinout.xyz/
# TODO make configurable, enhance with name, active high setting, local/remote GPIO
PIN_RELAYS = [6, 13, 19, 26]
# default relay index used for myStrom API emulation
DEF_RELAY = 2

# variables
notFoundResponse = HTTPResponse(body="<html><head><title>Error</title></head><body><h1>404 Not Found</h1></body></html>", 
                                status=404)
devices = []


# --- Emulate myStrom WiFi Switch API for the default relay -------------------
# https://mystrom.ch/wp-content/uploads/REST_API_SWI.txt
@get('/relay')
def onOff():
    if request.query.state == '1':
        devices[DEF_RELAY].on()
    elif request.query.state == '0':
        devices[DEF_RELAY].off()
    else:
        return notFoundResponse

@get('/toggle')
def toggle():
    devices[DEF_RELAY].toggle()

@get('/report')
def report():
    return {'relay': devices[DEF_RELAY].value}
# --- END myStrom WiFi Switch API ---------------------------------------------

@get('/relays')
def getOverview():
    overview = {'relays' : [] }
    for i in range(0, len(devices)):
        overview['relays'].append({i + 1: devices[i].value})
    return overview

@get('/relays/<relay>')
def getRelayState(relay):
    return {'relay': getDevice(relay).value}

@put('/relays/<relay>/toggle')
def toggle(relay):
    getDevice(relay).toggle()
    return getRelayState(relay)

@put('/relays/<relay>/on')
def switchOn(relay):
    getDevice(relay).on()

@put('/relays/<relay>/off')
def switchOff(relay):
    getDevice(relay).off()

def getDevice(relayNumber):
    if relayNumber.isdigit():
        index = int(relayNumber) - 1
        if index >= 0 and index < len(devices):
            return devices[index]
    raise notFoundResponse
    
    
# -- main

# initialize
parser = argparse.ArgumentParser(description="Relay board REST API",
                                 epilog="Control relays with REST API emulating the myStrom WiFi Switch API")
parser.add_argument("-l", "--loglevel", help="logging level", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default="INFO")
parser.add_argument("-lf", "--logfile", help="log file")
args = parser.parse_args()

if args.logfile:
    LOG_FILENAME = args.logfile

# Configure logging to log to a file and console
logger = logging.getLogger()
logger.setLevel(args.loglevel)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
logger.addHandler(consoleHandler)

if args.logfile:
    # Make a handler that writes to a file, making a new file at midnight and keeping some backups
    # based on: http://blog.scphillips.com/posts/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/
    handler = logging.handlers.TimedRotatingFileHandler(args.logfile, when="midnight", backupCount=10)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Make a class we can use to capture stdout and sterr in the log
    class RedirectLogger(object):
        def __init__(self, logger, level):
            """Needs a logger and a logger level."""
            self.logger = logger
            self.level = level

        def write(self, message):
            # Only log if there is a message (not just a new line)
            if message.rstrip() != "":
                self.logger.log(self.level, message.rstrip())

    # Replace stdout with logging to file at INFO level
    sys.stdout = RedirectLogger(logger, logging.INFO)
    # Replace stderr with logging to file at ERROR level
    sys.stderr = RedirectLogger(logger, logging.ERROR)

# start server
logger.info("Starting relay board REST API server")

# sets pins as outputs. Relay board is active low: i.e. relay is active when setting GPIO output to low
for pin in PIN_RELAYS:
    logger.debug("Initializing GPIO: %d", pin)
    # TODO configuration option for remote gpiozero configuration factory
    devices.append(OutputDevice(pin, active_high=False, initial_value=False))

try:
    # TODO make interface and port configurable
    run(host='0.0.0.0', port=8080, reloader=True, debug=(args.loglevel == 'DEBUG'))

# proper cleanup of background threads and GPIO settings, e.g. on ctrl+C
finally:
    for device in devices:
        device.close()
