# pi-power-switch
Control relay board with REST API on a Raspberry Pi


**Under development - current version is a proof of concept only!**


Tested with:
- Python 2.7.9
- [Bottle 0.12](http://bottlepy.org/)
- [gpiozero 1.4.0](https://gpiozero.readthedocs.io)
- Raspberry Pi 2 running Raspbian Jessie
- Noname ["Arduino 4 channel relay module board" from eBay](https://www.ebay.com/sch/Arduino+4+channel+relay+module+board)

## Features
- Control GPIO output pins with simple REST API
- One output emulates [myStrom WiFi Switch](https://mystrom.ch/wifi-switch/) [API](https://mystrom.ch/mystrom-for-developers/) for simple integration into other scripts
- Runs as system service (see scripts/init.d)


## Installation
1. Install bottle and gpiozero Python libraries: 
    ```
    pip install bottle
    sudo apt install python-gpiozero
    ```
1. Copy this file to /home/pi 

   or wherever you prefer, e.g. /usr/local/bin
1. Connect relay module board:
   * verify if relays are active high or low. Adapt Python script accordingly.
   * set BCM pin numbers in Python script
1. Install script as system service:

   if this script was not installed in /home/pi: change $DIR and $LOG_DIR in pi-power-api script.
    ```
    sudo copy ./scripts/init.d/pi-power-api /etc/init.d/
    sudo chmod 755 /etc/init.d/pi-power-api
    sudo update-rc.d pi-power-api defaults
    ```
1. Start daemon
    ```
    sudo service pi-power-api start
    ```
  
## TODO
- Externalize hard coded values into configuration file
- Support remote GPIO
- Simple web-interface 
