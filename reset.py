#!/usr/bin/python
# -*- coding: UTF-8 -*-


def reset():
    with open("/sys/class/gpio/gpio119/value", "r") as fd:
        value = fd.read()
    if '0' in value:
        print "reset button is pressing"
    elif '1' in value:
        print "reset button is not pressing"


def switch_1():
    with open("/sys/class/gpio/gpio124/value", "r") as fd:
        value = fd.read()
    if '0' in value:
        print "switch1 is on"
    elif '1' in value:
        print "switch1 is off"


def switch_2():
    with open("/sys/class/gpio/gpio121/value", "r") as fd:
        value = fd.read()
    if '0' in value:
        print "switch2 is on"
    elif '1' in value:
        print "switch1 is off"
