#!/usr/bin/python

import socket
import threading

acceptFrom = ["localhost"]
listenPort = 1201
network = 'nullstorm.r00t.la'
port = 6667
inSock = None
outSock = None
commSock = None

def __main__():
	commSock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	commSock.listen(listenPort)
	#output
	#connect
	irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
	irc.connect ( ( network, port ) )
	print irc.recv ( 4096 )
	irc.send ( 'NICK dicey\r\n' )
	irc.send ( 'USER dicey dicey dicey :Python IRC\r\n' )
	
	#main loop
	while True:
		data = irc.recv ( 4096 )
		if not data: break
		handleData(data)
		print data
		
	# start listening
	
class MyThread ( threading.Thread ):