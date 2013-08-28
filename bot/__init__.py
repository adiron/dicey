# bot.py - a bot object for IRC.
# version 1.0
# Copyright 2009 Adi Ron
# Served under the GPL.
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Just a few things:

# Arguments given to checkFuncs and actFuncs:
#	sender, args, txt 

# Internal command hooks: 
# Format: name(args) - description
# onQuit() - when quitting
# onConnect() - after connecting to the server

import socket

class bot():
	def __init__(self, master, channels, nick, user="PyBot"):
		self.master = master
		self.channels = channels
		self.nick = nick
		self.user = user
		self.commands = {}
		self.irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
		self.needToQuit = False
		self.inCommands = {}

	def register(self, checkFunc, actFunc, evtype = "PRIVMSG"):
		"registers actFunc to run if checkFunc is true"
		try:
			self.commands[evtype].append([checkFunc, actFunc])
		except KeyError:
			self.commands[evtype] = [[checkFunc, actFunc]]
			
	def internalRegister(self, func, evtype):
		"registers internal events."
		self.inCommands[evtype] = func
			
	def connect(self, server, port):
		self.server = server
		self.port = port
		self.irc.settimeout(280)
		self.irc.connect (( server, port ))
		self.irc.send ( b'NICK ' + bytes(self.nick, "UTF-8") + b'\r\n')
		self.irc.send ( b'USER ' + bytes(self.nick, "UTF-8") + b' ' + bytes(self.nick, "UTF-8") + b' ' + bytes(self.nick, "UTF-8") + b' :' + b' ' + bytes(self.user, "UTF-8") + b'\r\n' )
		try: self.inCommands["onConnect"]()
		except: pass
	
	def join(self, chan):
		self.irc.send ( b'JOIN ' + bytes(chan, "UTF-8") + b'\r\n')
		
	def start(self):
		"runs the bot."
		while True:
			try:
				data = self.irc.recv ( 4096 )
			except socket.timeout:
				# reconnect if we timed out
				self.irc.close()
				self.irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
				self.connect(self.server,self.port)
				data = self.irc.recv(4096)
				
			try: data = str(data,"UTF-8")
			except UnicodeDecodeError: data = str(data,"CP1252")
			if not data: break
			print (data)
			self.handleData(data)
		print ("Reconnecting...")
		if not self.needToQuit:
			self.irc.close()
			self.irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
			self.connect(self.server,self.port)
			self.start()
		else:
			try:
				self.inCommands["onQuit"]()
			except:
				pass
			finally:
				quit()
	# export the socket's function
	
	def handleData(self,data):
		# Send a ping back if we get one.
		if data.find ( 'PING' ) == 0:
			self.irc.send ( bytes('PONG ' + data.split()[1] + '\r\n', "UTF-8") )
		
		sep = data.split()
		if sep[0][0] == ":":
			sep[0] = sep[0][1:]
		
		sender = sep[0][0:sep[0].find("!")] # take the crap out of the names
		cmd = sep[1] # the IRC command
		args = []
		stop = 0
		for a in range(2,len(sep)):
			if sep[a][0] == ":":
				stop = a
				break
			else:
				args.append(sep[a])
		txt = " ".join(sep[stop:])[1:]
		
		# so we've figured out what our args are and so on.
		# let's let's start running those functions!
		
		try:
			for a in self.commands[cmd]: # the list of funcs registered for this IRC command
				if a[0](sender, args, txt):
					a[1](sender, args, txt)
		except KeyError:
			self.commands[cmd] = list()
		
		
		