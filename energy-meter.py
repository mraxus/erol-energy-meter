#!/usr/bin/env python2.7
# script based on Alex Eames https://raspi.tv
# https://raspi.tv/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3

from datetime import datetime
import json
import os.path
import time

import RPi.GPIO as GPIO

FILE_PATH = "/home/pi/EnergyMeter/data.json"

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

blink = 0


def interrupt(_):
    global blink
    blink = blink + 1
    print ("Energy pulse recorded")


GPIO.add_event_detect(24, GPIO.RISING, callback=interrupt, bouncetime=300)


def fix_date(date):
    encoded = json.loads(json.dumps(date, default=str))
    return 'T'.join(encoded.split(' ')) + 'Z'


def read_data():
    if os.path.isfile(FILE_PATH):
        file = open(FILE_PATH, "r")
        raw_data = file.read()
        file.close()
        return json.loads(raw_data)
    else:
        return {
            "DateTime": fix_date(datetime.utcnow()),
            "ActivePower": 0,
            "RealEnergy": 0,
            "RealEnergyPerHour": 0
        }


def write_data(active_power, real_energy):
    raw_data = json.dumps({
        "DateTime": fix_date(datetime.utcnow()),
        "ActivePower": active_power,
        "RealEnergy": real_energy,
        "RealEnergyPerHour": 0
    })
    file = open(FILE_PATH, "w")
    file.write(raw_data)
    file.close()


def calc():
    global blink
    active_power = 0 if blink == 0 else int(1000 / (60.0 / blink / 36))

    # Reset blink
    blink = 0

    old_data = read_data()
    real_energy = old_data['RealEnergy'] + (active_power / 60)

    write_data(active_power, real_energy)
    print 'new data: %d' % active_power


try:
    while True:
        time.sleep(60)
        calc()
except KeyboardInterrupt:
    GPIO.cleanup()  # clean up GPIO on CTRL+C exit
