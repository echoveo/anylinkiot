#!/usr/bin/python
# -*- coding: UTF-8 -*-


import os
import datetime
import ntplib

# ntp servers
ntp_servers = ["pool.ntp.org", "0.pool.ntp.org", "1.pool.ntp.org", "2.pool.ntp.org"]

c = ntplib.NTPClient()
for server in ntp_servers:
    try:
        response = c.request(server)
        if response:
            ts = response.tx_time
            _date, _time = str(datetime.datetime.fromtimestamp(ts))[:22].split(' ')

            # set time
            os.system('date -s "%s %s"' % (_date, _time))
            print "Set successfully"
            break
    except ntplib.NTPException as e:
        print repr(e)

