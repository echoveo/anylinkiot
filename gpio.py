#!/usr/bin/python
# -*- coding: UTF-8 -*-


import serial
import os
import time

gPortDict = {'RS232': '/dev/ttymxc6', 'RS485-1': '/dev/ttymxc1', 'RS485-2': '/dev/ttymxc2'}
gParity = {'O': serial.PARITY_ODD, 'N': serial.PARITY_NONE, 'E': serial.PARITY_EVEN}
gStopbits = {'1': serial.STOPBITS_ONE, '2': serial.STOPBITS_TWO}
gDatabits = {'5': serial.FIVEBITS, '6': serial.SIXBITS, '7': serial.SEVENBITS, '8': serial.EIGHTBITS}

gGPIO_INPUT = "/sys/class/gpio/gpio117/value"
gGPIO_OUTPUT = "/sys/class/gpio/gpio118/value"


def serial_test(port, baud, parity, databits, stopbit, sdata):
    global gPortDict, gParity, gStopbits, gDatabits
    fd = None
    try:
        fd = serial.Serial(gPortDict[port], baudrate=baud, bytesize=gDatabits[databits], parity=gParity[parity],
                           stopbits=gStopbits[stopbit], timeout=0.5)
        print "send data:%s" % sdata
        fd.write(sdata)
        data = fd.readall()
        if not data  or len(data) == 0:
            print "no response data"
        else:
            print "receive data:%s" % data
    except Exception as e:
        print repr(e)
    finally:
        if fd:
            fd.close()


def test_serial_port():
    """test serial port"""
    global gPortDict
    data = "this is serial test."
    for port in gPortDict:
        print "start check %s" % port
        serial_test(port, 9600, 'N', '8', '1', data)
        print "finish"
        time.sleep(1)


def set_output(val):
    global gGPIO_OUTPUT
    try:
        os.system("echo %s > %s" % (val, gGPIO_OUTPUT))
    except Exception as e:
        print repr(e)


def get_input():
    global gGPIO_INPUT
    with open(gGPIO_INPUT, "r") as fd:
        content = fd.read()
        if "1" in content:
            print "input signal is exist"
        elif "0" in content:
            print "input signal is not exist"
        else:
            print "input error!"


def test_gpio():
    """test gpio"""
    print "set gpio output 1"
    set_output(1)
    time.sleep(1)
    print "set gpio output 0"
    set_output(0)

    print "get gpio input status"
    get_input()


if __name__ == '__main__':
    test_serial_port()
    test_gpio()
