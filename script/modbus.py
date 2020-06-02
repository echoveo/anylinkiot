#!/usr/bin/python
import serial
import sys
import os


par = {'O':serial.PARITY_ODD,'N':serial.PARITY_NONE,'E':serial.PARITY_EVEN}
stp = {'1':serial.STOPBITS_ONE,'2':serial.STOPBITS_TWO}
bys = {'5':serial.FIVEBITS,'6':serial.SIXBITS,'7':serial.SEVENBITS,'8':serial.EIGHTBITS}


def crc16(l , n):
	reg_crc = 0xffff
	while n:
		reg_crc ^= l[-n]
		for i in range(8):
			if reg_crc & 0x01:
				reg_crc = (reg_crc >> 1) ^ 0xa001
			else:
				reg_crc = reg_crc >> 1
		n = n-1
	return reg_crc % 256, reg_crc / 256

def lrc(l):
	return 0xff & (0xff +1 -sum(l))

def getascii(l):
	def turn(x):
		print 'turn x = ',x
		if x >=0 and x<=9:
			return x+0x30
		else:
			return ord('a')+x-10
	data =':'
	li = l[:2]
	for i in range(2):
		li.append(l[i+2] / 256)
		li.append(l[i+2] % 256)
	li.append(lrc(li))
	for i  in range(len(li)):
		data += chr(turn(li[i] / 16)) + chr(turn(li[i] % 16))
	data += chr(0x0d)+chr(0x0a)
	return data

def getrtu(l):  #slave func addr num
	li = l[:2]
	for i in range(2):
		li.append(l[i+2] / 256)
		li.append(l[i+2] % 256)
	crc_h, crc_l = crc16(li, len(li))
	li.append(crc_h)
	li.append(crc_l)
	return ''.join([chr(i) for i in li])

def readconfig():
	result = list()
	for line in open('/opt/.serialconf','a+').readlines():
		result.append(line.strip())
	if len(result) == 0:
		l = ['/dev/ttyO4','9600','N','8','1']
		open('/opt/.serialconf','w').write("%s" % '\n'.join(l))
		return l
	return result

def setconfig(l):
	if len(l) == 5:
	    open('/opt/.serialconf','w').write("%s" % '\n'.join(l))
	elif len(l) == 4:
		l.insert(0, '/dev/ttyO4')
		open('/opt/.serialconf','w').write("%s" % '\n'.join(l))

def help():
	print '''
redbudtek  tx
usage: modbus [options] data

send modbus rtu / ascii respond to an serial port and read the request

options:
	-h  	help information
	-r		like './modbus -r slaveid function_code addr num     |    ./modbus -r 1 3 0000 0008'
	-a  	like './modbus -a slaveid function_code addr num     |    ./modbus -a 1 3 0000 0008'
	-sh  	send message as hex                                  |    ./modbus -s 01 03 00 00 00 01 84 0a
	-sa     send message as ascii                                |    ./modbus abcdefg
	-c      config the serial port     the config will be saved  |	  ./modbus -c 9600 n 8 1  (baud,parity,bytes,stopbits)
			the default port is /dev/ttyo4						 |	  ./modbus -c /dev/ttyUSB0	9600 n 8 1 
	-sc      show current serial port config                     |    ./modbus -sc
	'''
def serialtest(port,baud,parity,databits,stopbit,sdata):
	fd = None
	try:
		fd = serial.Serial(port,baudrate=baud, bytesize=bys[databits],parity=par[parity],stopbits=stp[stopbit],timeout=0.5)
		print 'open port at'+str([port,baud,parity,databits,stopbit])
		print sdata
		for i in range(len(sdata)):
				print hex(ord(sdata[i])),
		print '\n'
		while True:
			fd.write(sdata)
			print 'write.....',
			for i in range(len(sdata)):
				print hex(ord(sdata[i])),
			print '\n'
			data = fd.readall()
			if data:
				print 'recv...... ',
				for i in range(len(data)):
					print hex(ord(data[i])),
				print '\n'
	except Exception as e:
		print e

if __name__=='__main__':
	conf = readconfig()
	argv_len = len(sys.argv)
	if argv_len == 1:
		help()
		exit(0)
	elif argv_len == 2:
		if sys.argv[1] == '-h':
			help()
		elif sys.argv[1] == '-sc':
			print 'current serial config is'+ str(conf)+'\n'
		else:
			print 'wrong oprion '
	elif argv_len > 2:
		if sys.argv[1] == '-a' or sys.argv[1] == '-r':
			if len(sys.argv) != 6:
				print 'args wrong '
				exit(0)
			else:
				li =list()
				try:
					li.append(int(sys.argv[2]))
					li.append(int(sys.argv[3]))
					if sys.argv[4].startswith('0x') or sys.argv[4].startswith('0x'):
						li.append(int(sys.argv[4],16))
					else:
						li.append(int(sys.argv[4]))
					li.append(int(sys.argv[5]))
				except Exception as e:
					print e
			if sys.argv[1] == '-a':
				serialtest(conf[0], int(conf[1],10), conf[2], conf[3], conf[4], getascii(li))
			else:
				serialtest(conf[0], int(conf[1],10), conf[2], conf[3], conf[4], getrtu(li))
		elif sys.argv[1] == '-sh':
			serialtest(conf[0], int(conf[1],10), conf[2], conf[3], conf[4],''.join([ chr(int(i,16)) for i in sys.argv[2:] ]))
		elif sys.argv[1] == '-sa':
			serialtest(conf[0], int(conf[1],10), conf[2], conf[3], conf[4], ''.join(sys.argv[2:]))
		elif sys.argv[1] == '-c':
			print 'set serial config to \n',sys.argv[2:]
			setconfig(sys.argv[2:])