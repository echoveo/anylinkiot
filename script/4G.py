#!/usr/bin/python
# -*- coding: UTF-8 -*-


import os
import sys
import time
import serial
import xml.etree.ElementTree as ET
operator_path = "/home/ie/operatorinfo.xml"
# Network operator information
APNList = {"name": "CHINA-MOBILE",
           "imsi": ["46000", "46004"],
           "usr": "none",
           "passwd": "none",
           "apn": "cmiot"}

# Network mode
networkmode = {'0': 'no service', '1': 'GSM', '2': 'GPRS', '3': 'EDGE', '4': 'WCDMA', '5': 'HSDPA', '6': 'HSUPA',
               '7': 'HSPA', '8': 'LTE', '9': 'TDS-CDMA',
               '10': 'TDS-HSDPA', '11': 'TDS-HSUPA', '12': 'TDS-HSPA', '13': 'CDMA', '14': 'EVDO', '15': 'HYBRID',
               '16': '1XLTE', '23': 'eHRPD', '24': 'HYBRID'}


def power_module():
    os.system("echo 69 > /sys/class/gpio/export")
    os.system("echo out > /sys/class/gpio/gpio69/direction")
    os.system("echo 1 > /sys/class/gpio/gpio69/value")
    return 0


def info_operator():
    tree = ET.parse(operator_path)
    operatorinfo_nodes = tree.findall('operator_Remote/operator_List/operator_Info')
    operator_list = []
    if len(operatorinfo_nodes) < 1:
        return operator_list

    for operatorinfo_node in operatorinfo_nodes:
        operator_info = dict()
        operator_name = operatorinfo_node.find('name').text
        if operator_name is None:
            operator_name = 'new_operator'
        operator_imsi = operatorinfo_node.find('imsi').text
        if operator_imsi is None:
            operator_imsi = 'None'
        operator_usr = operatorinfo_node.find('usr').text
        if operator_usr is None:
            operator_usr = 'None'
        operator_passwd = operatorinfo_node.find('passwd').text
        if operator_passwd is None:
            operator_passwd = 'None'
        operator_apn = operatorinfo_node.find('apn').text
        if operator_apn is None:
            operator_apn = 'None'
        operator_info['name'] = operator_name
        operator_info['imsi'] = operator_imsi
        operator_info['usr'] = operator_usr
        operator_info['passwd'] = operator_passwd
        operator_info['apn'] = operator_apn
        operator_list.append(operator_info)

    return operator_list


# 4G module operation
class BaseAction(object):

    def __init__(self):
        time.sleep(1)

    @staticmethod
# Serial operation
    def _serial_usb(tx):
        try:
            fd = serial.Serial('/dev/ttyUSB2', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=5)
            fd.write(tx+'\r\n')
            recv = fd.readall()
        except Exception as e:
            print "Serial action failed, msg: " + repr(e)
            return None
        else:
            if not fd:
                fd.close()
            return recv

# Detecting 4G modules
    def sync_module(self):
        recv = self._serial_usb('AT')
        if recv and 'OK' in recv:
            return True
        else:
            print recv
            return False

# Detect SIM card
    def get_cpin(self):
        recv = self._serial_usb('AT+CPIN?')
        if recv and 'READY' in recv:
            return True
        else:
            return False

# Obtaining the operator identity from the SIM card
    def get_imsi(self):
        imsi = -1
        recv = self._serial_usb('AT+CIMI')
        if recv and 'OK' in recv:
            try:
                imsi = recv[recv.index('\r\n') + 2:]
                imsi = imsi[0:5]
                return imsi
            except Exception as e:
                print "Get IMSI failed, msg: " + repr(e)
                return imsi
        else:
            return imsi

# Set the 4G module dial mode to automatic
    def set_cnsmod(self):
        recv = self._serial_usb('AT+CNSMOD=1')
        if recv and 'OK' in recv:
            return True
        else:
            return False

# Read network mode
    def get_cnsmod(self):
        recv = self._serial_usb('AT+CNSMOD?')
        if recv and 'OK' in recv:
            try:
                cnsmod = recv[recv.index('+CNSMOD:') + 11:]
                cnsmod = cnsmod[:cnsmod.index('\r\n')]
                return cnsmod
            except Exception as e:
                print "Get cnsmod failed, msg: " + repr(e)
                return False
        else:
            return False

# Read network strength
    def get_csq(self):
        recv = self._serial_usb('AT+CSQ')
        if recv and 'OK' in recv:
            try:
                csq = recv[recv.index('+CSQ:') + 6:]
                csq = csq[:csq.index(',')]
                return int(csq)
            except Exception as e:
                print "Get csq failed, msg: " + repr(e)
                return False
        else:
            return False

# GPRS network registration status
    def get_cgreg(self):
        recv = self._serial_usb('AT+CGREG?')
        if recv and ('0,1' in recv or '0,5' in recv):
            return True
        else:
            return False

# EPS network registration status
    def get_cereg(self):
        recv = self._serial_usb('AT+CEREG?')
        if recv and ('0,1' in recv or '0,5' in recv):
            return True
        else:
            return False

# Define PDP context
    def set_cgdcont(self, apn):
        recv = self._serial_usb('AT+CGDCONT=1,"IP","%s"' % apn)
        if recv and 'OK' in recv:
            return True
        else:
            return False

# Set type of authentication for PDP-IP connections of GPRS
    def set_cgauth(self, passwd, usrname):
        recv = self._serial_usb('AT+CGAUTH=1,3,"%s","%s"' % (passwd, usrname))
        if recv and 'OK' in recv:
            return True
        else:
            return False

# Start network dial
    def set_qcrmcall(self, onoff):
        recv = self._serial_usb('AT$QCRMCALL=%s,1' % onoff)
        if recv and 'OK' in recv:
            return True
        else:
            return False

# Get dial results
    def get_qcrmcall(self):
        recv = self._serial_usb('AT$QCRMCALL?')
        if recv and '1, V4' in recv:
            return True
        else:
            return False

# Read ICCID from SIM card
    def get_iccid(self):
        recv = self._serial_usb('AT+CICCID')
        if recv and 'OK' in recv:
            try:
                iccid = recv[recv.index('+ICCID:') + 8:]
                iccid = iccid[:iccid.index('\r\n')]
                return iccid
            except Exception as e:
                print "Get iccid failed, msg: " + repr(e)
                return False
        else:
            return False

# Read ip address
    @staticmethod
    def get_ifaddr(ifname):
        import socket
        import fcntl
        import struct
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ifaddr = fcntl.ioctl(sock.fileno(), 0x8915, struct.pack('256s', ifname[:15]))
            return socket.inet_ntoa(ifaddr[20:24])
        except Exception, e:
            print repr(e)
            return False


class SIM7600Action(object):
    def __init__(self):
        self._base_action = BaseAction()

# Check module and SIM card status before dialing
    def init(self):
        readimsi = False
        operator_list = info_operator()
        if not self._base_action.sync_module():
            print "AT module Failed"
            return False
        if not self._base_action.get_cpin():
            print "SIM card is not ready"
            return False
        if not self._base_action.set_cnsmod():
            print "Set auto report network system mode failed"
            return False
        imsi = self._base_action.get_imsi()
        for operatorinfo in operator_list:
            if imsi in operatorinfo["imsi"]:
                readimsi = True
                break
        if not readimsi:
            print "operator error"
        net_mode = self._base_action.get_cnsmod()
        if not net_mode or 'no service' in networkmode[net_mode]:
            print "Network mode error"
            return False
        csq = self._base_action.get_csq()
        if not csq or csq < 1 or csq > 31:
            print "Signal strength is not a normal value"
            return False

        if 'LTE' in networkmode[net_mode]:
            if not self._base_action.get_cereg:
                print "EPS network registered failed"
                return False
        else:
            if not self._base_action.get_cgreg:
                print "GPRS network registered failed"
                return False

        return True

# Set up network operator information
    def set_apn(self):
        apn = 'cmiot'
        username = 'none'
        password = 'none'
        operator_list = info_operator()
        imsi = self._base_action.get_imsi()
        if imsi == -1:
            return False
        for operatorinfo in operator_list:
            if imsi in operatorinfo['imsi']:
                apn = operatorinfo['apn']
                username = operatorinfo['usr']
                password = operatorinfo['passwd']

        if not self._base_action.set_cgdcont(apn):
            return False
        print 'Set APN %s' % apn
        if username is not 'none' and not self._base_action.set_cgauth(password, username):
            return False
        print 'set usrname %s, password %s' % (username, password)
        return True

# Start network dial
    def start_dial(self):
        if not self._base_action.set_qcrmcall('1'):
            return False
        if not self._base_action.get_qcrmcall():
            return False
        return True

# Stop network dial
    def stop_dial(self):
        if not self._base_action.set_qcrmcall('0'):
            return False
        return True

# Dial until you succeed
    def run(self):
        while True:
            if not self.start_dial():
                print 'qcrmcall failed'
                self.stop_dial()
                time.sleep(30)
                continue
            os.system('/sbin/udhcpc -i wwan0 -t 5 -n -q &')
            time.sleep(30)
            ifaddr = self._base_action.get_ifaddr('wwan0')
            if ifaddr:
                print 'wwan0 inet addr %s obtained' % ifaddr
                break


if __name__ == '__main__':
    power_module()
    time.sleep(5)
    os.system("systemctl stop ModemManager.service")
    time.sleep(2)
    dial = SIM7600Action()
    if not dial.init():
        sys.exit(1)

    if not dial.set_apn():
        sys.exit(2)

    dial.run()
