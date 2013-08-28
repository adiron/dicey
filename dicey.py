#!/usr/local/bin/python3.1
import random
import pickle
import math
import code, traceback, signal
import bot
import threading
import os
import sys

# Console on SIGUSR1
def debug(sig, frame):
	d={'_frame':frame}		 # Allow access to frame object.
	d.update(frame.f_globals)  # Unless shadowed by global
	d.update(frame.f_locals)

	i = code.InteractiveConsole(d)
	message  = "Signal recieved : entering python shell.\nTraceback:\n"
	message += ''.join(traceback.format_stack(frame))
	i.interact(message)

#def listen():
#	signal.signal(signal.SIGUSR1, debug)  # Register handler

# check generators. Very useful.
def simpleCheck(command):
	return (lambda sender, args, txt: command == txt.split()[0])
def masterCheck(command):
	return (lambda sender, args, txt: (command == txt.split()[0]) & (sender == irc.master))
				

safe_dict = dict()
safe_dict['abs'] = abs
safe_dict['rnd'] = random.randint
safe_dict['pi'] = math.pi
safe_dict['sqrt'] = math.sqrt
safe_dict['floor'] = math.floor
safe_dict['pow'] = math.pow
safe_dict['ceil'] = math.ceil
safe_dict['math'] = math

#Section 1: Variable

network = 'irc.nullstorm.r00t.la'
port = 6667
channels = ["#aubcom", "#nullstorm", "#aubcom-dnd"]
channel = "#aubcom" # primary channel for !j and !p
nick = "dicey"
chars = {}
hp = {}

CharPickleFile = "chars.pickle"
HPPickleFile = "hp.pickle"

# Init the bot module.

irc = bot.bot(master="dushkin", channels=channels, nick=nick)

#Section 2: Functions

def TextEval(txt):
	# Evaluates text as math expression
	return float(eval(txt,{"__builtins__":None},safe_dict))
	
def Modifier(a):
	return math.floor((a-10)/2)
	
def findKey(dic, val):
	for a in dic.items():
		if v == val: return k


def saveChars(a):
	# Pickle and dump all chars.
	try:
		# This will create a new file or **overwrite an existing file**.
		f = open(CharPickleFile, "wb")
		try:
			pickle.dump(a,f) # Write a string to a file
		finally:
			f.close()
	except IOError:
		pass

def readChars():
	retVal = {}
	try:
		f = open(CharPickleFile, "rb")
		try:
			# Read the entire contents of a file at once.
			retVal = pickle.load(f)
		finally:
			f.close()
	except IOError:
		pass
	return retVal
	
def saveHP(a):
	# Pickle and dump all chars.
	try:
		# This will create a new file or **overwrite an existing file**.
		f = open(HPPickleFile, "wb")
		try:
			pickle.dump(a,f) # Write a string to a file
		finally:
			f.close()
	except IOError:
		pass

def readHP():
	retVal = {}
	try:
		f = open(HPPickleFile, "rb")
		try:
			# Read the entire contents of a file at once.
			retVal = pickle.load(f)
		finally:
			f.close()
	except IOError:
		pass
	return retVal	


def sendMsg(recp, txt):
	irc.irc.send(bytes("PRIVMSG " + recp + " :" + txt + "\r\n","UTF-8"))
	
def toCommands(txt):
	cmds = txt[1:len(txt)].strip().split(" ")
	commands = []
	for a in cmds: # now we need to clean up the list
		if a != "":
			commands.append(a)
	return commands

# Register all the commands:

def func_cmd(sender, args, txt):
	commands = toCommands(txt)
	try:
		irc.irc.send(bytes(" ".join(commands[1:]) + "\r\n","UTF-8"))
	except IndexError:
		sendMsg(dushkin, "Commands plx.")
			
def check_cmd(sender, args, txt):
	if (txt.find("!cmd") == 0) and (sender == master) and (args[0] == nick): return True
	else: return False
	
def func_urls(sender, args, txt):
	recp = args[0]
	output = ""
	for k,v in chars.items():
		output = output + k + " as " + "http://auberdine.com/wiki/index.php/" + v.replace(" ", "_") 
	if output == "": output = "Nothing!"
	sendMsg(sender, output)
	
def check_chars(sender, args, txt):
	commands = toCommands(txt.lower())


def func_chars(sender, args, txt):
	recp = args[0]
	commands = toCommands(txt.lower())
	try:
		output = commands[1] + " as " + chars[commands[1]] + ". (" + str(hp[commands[1]][0]) + "/" + str(hp[commands[1]][1]) + ")"
	except IndexError:
		output = ""
		for k,v in chars.items():
			output = output + k + " as: " + v + " (" + str(hp[k][0]) + "/" + str(hp[k][1]) + ").  "
	except KeyError:
		output = "No such binding."
	if output == "": output = "Nothing!"
	if recp[0] == "#":
		sendMsg(recp, output)
	else:
		sendMsg(sender, output)
	print( chars)
		
def func_heal(sender, args, txt):
	recp = args[0]
	commands = toCommands(txt.lower())
	try:
		overheal = 0
		target = commands[1].lower()
		a=int(commands[2])
		hp[target][0] = hp[target][0] + a
		overheal = hp[target][0] - hp[target][1]
		if hp[target][0] > hp[target][1]:
			hp[target][0] = hp[target][1]
		print( hp)
		display = chars[target] + " gained " + str(a) + " HP. Now has " + str(hp[target][0]) + "/" + str(hp[target][1]) + "."
		if overheal > 0:
			display = display + " (" + str(overheal) + " overheal)." 
		if hp[target][0] == 0:
			display = display + "  DISABLED!"
		if (hp[target][0] < 0) and (hp[target][0] >= -9):
			display = display + "  DYING!"
		if hp[target][0] <= -10:
			display = display + "  DEAD!"
			
			
		if recp[0] == "#":
			sendMsg(recp, display)
		else:
			sendMsg(sender, display)
			
	except ValueError: # not a number
		if recp[0] == "#":
			sendMsg(recp, "Not a number.")
		else:
			sendMsg(sender, "Not a number.")
	except KeyError: # no such player
		if recp[0] == "#":
			sendMsg(recp, "No such player.")
		else:
			sendMsg(sender, "No such player.")
	except IndexError: # more arguments
		if recp[0] == "#":
			sendMsg(recp, "Need more arguments.")
		else:
			sendMsg(sender, "Need more arguments.")
			
	saveChars(chars)
	saveHP(hp)

def func_harm(sender, args, txt):
	recp = args[0]
	commands = toCommands(txt.lower())
	try:
		target = commands[1].lower()
		a=int(commands[2])
		hp[target][0] = hp[target][0] - a
		print( hp)
		display = chars[target] + " lost " + str(a) + " HP. Now has " + str(hp[target][0]) + "/" + str(hp[target][1]) + "."				
		if hp[target][0] == 0:
			display = display + "  DISABLED!"
		if (hp[target][0] < 0) and (hp[target][0] >= -9):
			display = display + "  DYING!"
		if hp[target][0] <= -10:
			display = display + "  DEAD!"
			
		if recp[0] == "#":
			sendMsg(recp, display)
		else:
			sendMsg(sender, display)
			
	except ValueError: # not a number
		if recp[0] == "#":
			sendMsg(recp, "Not a number.")
		else:
			sendMsg(sender, "Not a number.")
	except KeyError: # no such player
		if recp[0] == "#":
			sendMsg(recp, "No such player.")
		else:
			sendMsg(sender, "No such player.")
	except IndexError: # more arguments
		if recp[0] == "#":
			sendMsg(recp, "Need more arguments.")
		else:
			sendMsg(sender, "Need more arguments.")

	saveChars(chars)
	saveHP(hp)
		
def func_sethp(sender, args, txt):
	recp = args[0]
	commands = toCommands(txt.lower())
	target = sender.lower()
	try: target = commands[2].lower()
	except IndexError: pass
	
	try:
		hp[target][0] = int(commands[1])
		# assuming success here
		if recp[0] == "#":
			sendMsg(recp, "Current HP of character " + chars[target] + " now " + commands[1] + ".")
		else:
			sendMsg(sender, "Current HP of character " + chars[target] + " now " + commands[1] + ".")
		saveHP(hp)
		saveChars(chars)
	except ValueError: # not a number
		if recp[0] == "#":
			sendMsg(recp, "Not a number.")
		else:
			sendMsg(sender, "Not a number.")
	except KeyError: # no such player
		if recp[0] == "#":
			sendMsg(recp, "No such player.")
		else:
			sendMsg(sender, "No such player.")

def check_sethp(sender, args, txt):
	if (txt.split()[0].lower() == "!sethp"):
		return True
	else:
		return False


def func_setmaxhp(sender, args, txt):
	commands = toCommands(txt.lower())
	recp = args[0]
	target = sender
	try:
		target = commands[2]
	except IndexError:
		pass

	try:
		hp[target][1] = int(commands[1])
		# assuming success here
		if recp[0] == "#":
			sendMsg(recp, "Max HP of character " + chars[target] + " now " + commands[1] + ".")
		else:
			sendMsg(sender, "Max HP of character " + chars[target] + " now " + commands[1] + ".")
		saveHP(hp)
		saveChars(chars)
	except ValueError: # not a number
		if recp[0] == "#":
			sendMsg(recp, "Not a number.")
		else:
			sendMsg(sender, "Not a number.")
	except KeyError: # no such player
		if recp[0] == "#":
			sendMsg(recp, "No such player.")
		else:
			sendMsg(sender, "No such player.")
		
def func_hp(sender, args, txt):
	recp = args[0]
	commands = toCommands(txt.lower())
	target = sender.lower()
	try: target = commands[1].lower()
	except IndexError: pass
	
	display = ""
	try:
		display = chars[target] + " has " + str(hp[target][0]) + " out of " + str(hp[target][1]) + " hit points."
		
		if hp[target][0] == 0:
			display = display + "  DISABLED!"
		if (hp[target][0] < 0) and (hp[target][0] >= -9):
			display = display + "  DYING!"
		if hp[target][0] <= -10:
			display = display + "  DEAD!"
			
		if recp[0] == "#":
			sendMsg(recp, display)
		else:
			sendMsg(sender, display)
			
	except KeyError: # when we can't find the player
		if recp[0] == "#":
			sendMsg(recp, "No such player.")
		else:
			sendMsg(sender, "No such player.")
	except IndexError:
		if recp[0] == "#":
			sendMsg(recp, "Not enough arguments.")
		else:
			sendMsg(sender, "Not enough arguments.")

def check_hp(sender, args, txt):
	if (txt.split()[0].lower() == "!hp") or (txt.split()[0].lower() == "!life"):
		return True
	else:
		return False
	
		
def func_bind(sender, args, txt):
	txt = " ".join(txt.split()[1:])
	if txt is not "": # if arg2 not empty, proceed to add
		chars[sender.lower()]=txt
		hp[sender.lower()] = [0,0] # cur,max
		
	else: # else remove
		chars.pop(sender.lower())
		hp.pop(sender.lower())
	print( chars)
	print( hp)
	saveChars(chars)
	saveHP(hp)
	
def func_purge(sender, args, txt):
		hp.clear()
		chars.clear()
		print (chars)
		print(hp)
		saveChars(chars)
		saveHP(hp)
		
def func_unbind(sender, args, txt):
	commands = toCommands(txt.lower())
	try:
		chars.pop(commands[1].lower())
		hp.pop(commands[1].lower())
		sendMsg(irc.master, commands[1] + " removed from bindings.")
		print(chars)
		print(hp)
		saveChars(chars)
		saveHP(hp)
	except IndexError: sendMsg(irc.master, "Need a name.")
	
def func_eval(sender, args, txt):
	commands = toCommands(txt.lower())
	try:
		sendMsg(sender, "Result: %2.4f" % TextEval(" ".join(commands[1:])))
	except NameError:
		#can't call that function
		sendMsg(sender, "Can't call that function.")
		
	except SyntaxError:
		#syntax error
		sendMsg(sender, "Syntax error.")
	
	except ValueError:
		#doesn't look like numbers
		sendMsg(sender, "Are these numbers?")
		
	except TypeError:
		#doesn't look like numbers
		sendMsg(sender, "Are these numbers?")
		
	except RuntimeError:
		#doesn't look like numbers
		sendMsg(sender, "Are you trying to make me crash?")
		
	except OverflowError:
		#overflow
		sendMsg(sender, "cool story bro")
		
	except:
		sendMsg(sender, "Encountered some kind of error.")
		
def func_mod(sender, args, txt):
	commands = toCommands(txt.lower())
	try:
		a = Modifier(int(commands[1]))
		sendMsg(sender, "Modifier for %s: %+0d" % (commands[1], a))
	except TypeError:
		sendMsg(sender, "Number error.")
	except ValueError:
		sendMsg(sender, "Number error.")

def func_part(sender, args, txt):
	'''Leaves a channel.'''
	commands = toCommands(txt.lower())
	try:
		irc.irc.send(bytes("PART " + commands[1] + "\r\n","UTF-8"))
	except IndexError:
		irc.irc.send(bytes("PART " + channel + "\r\n","UTF-8"))
		
def func_join(sender, args, txt):
	commands = toCommands(txt.lower())
	try:
		irc.irc.send(bytes("JOIN " + commands[1] + "\r\n","UTF-8"))
	except IndexError:
		irc.irc.send(bytes("JOIN " + channel + "\r\n","UTF-8"))
		
def func_roll(sender, args, txt):
	commands = toCommands(txt.lower())
	recp = args[0]
	try:
		commands[1] = commands[1].lower()
	except IndexError:
		if recp[0] == "#":
			sendMsg(recp, "Could not roll such dice. Check your syntax, " + sender + ".")
		else:
			sendMsg(sender, "Could not roll such dice. Check your syntax.")
		return
		return
	dice = commands[1].split("d")
	if dice[0] == "":
		dice[0] = 1
	try:
		dice[0] = int(dice[0])
		dice[1] = dice[1].replace("%","100")
		dice[1] = int(dice[1])
	except ValueError:
		if recp[0] == "#":
			sendMsg(recp, "Could not roll such dice. Check your syntax, " + sender + ".")
		else:
			sendMsg(sender, "Could not roll such dice. Check your syntax.")
		return
	except IndexError:
		dice.insert(0,1)
	
	rolls = []
	try:
		if dice[0] > 20:
			raise OverflowError
		if dice[1] > 200:
			raise OverflowError
		for a in range(0,dice[0]):
			rolls.append(random.randint(1,dice[1]) )
	except OverflowError:
		if recp[0] == "#":
			sendMsg(recp, "Could not roll such dice. Lower numbers please, " + sender + ".")
		else:
			sendMsg(sender, "Could not roll such dice. Lower numbers please.")
		return
	except ValueError:
		if recp[0] == "#":
			sendMsg(recp, "Could not roll such dice. Check your syntax, " + sender + ".")
		else:
			sendMsg(sender, "Could not roll such dice. Check your syntax.")
		return
	
	eq = ""
	for a in range(0,len(rolls)):
		eq = eq + str(rolls[a])
		if a != len(rolls) -1:
			eq = eq+" + "
	
	if recp[0] == "#":
		sendMsg(recp, sender + " rolled " + str(dice[0]) + "d" + str(dice[1]) + " for: " + str(sum(rolls)) + " (" + eq + ")")
	else:
		sendMsg(sender, "You rolled " + str(dice[0]) + "d" + str(dice[1]) + " for: " + str(sum(rolls))+ " (" + eq + ")")

def trackNickChange(sender, args, txt):
	'''Track nick changes.'''
	# New name is txt, old name is sender.
	if sender == irc.master:
		irc.master = txt
## TODO: fix this shit...
#	hp[txt.lower()] = hp[sender.lower()]
#	chars[txt.lower()] = chars[sender.lower()]
##	del hp[txt.lower()]
##	del chars[txt.lower()]
#	saveChars(chars)
#	saveHP(hp)
#		
def onQuit():
	saveHP(hp)
	saveChars(chars)
	
def func_quit(a,b,c):
	irc.needToQuit = True
	onQuit()
	quit()
	
def onConnect():
	for a in channels:
		irc.join(a)

	
#def func_version(sender, args, txt):
#	'''Responds to version requests.'''
	## "Python " + sys.version.replace("\n", "")
	## ^ Send this stuff.
# irc.register(simpleCheck("!quit"), (lambda sender, args, txt: sendMsg(args[0], "NO U.") ))
irc.register(masterCheck("!cmd"), func_cmd)
irc.register(simpleCheck("!urls"), func_urls)
irc.register(simpleCheck("!chars"), func_chars)
irc.register(simpleCheck("!heal"), func_heal)
irc.register(simpleCheck("!harm"), func_harm)
irc.register(simpleCheck("!setmaxhp"), func_setmaxhp)
irc.register(simpleCheck("!sethp"), func_sethp)
irc.register(check_hp, func_hp)
irc.register(simpleCheck("!bind"), func_bind)
irc.register(masterCheck("!purge"), func_purge) 
irc.register(masterCheck("!unbind"), func_unbind)
#irc.register(simpleCheck("!eval"), func_eval)
irc.register(simpleCheck("!mod"), func_mod)
irc.register(masterCheck("!part"), func_part)
irc.register(masterCheck("!join"), func_join)
irc.register(simpleCheck("!roll"), func_roll)
irc.register((lambda a,b,c: True) , trackNickChange, "NICK")
irc.register((lambda a,b,c: True) , onQuit, "onQuit")
irc.register(masterCheck("!quit"), func_quit)
#irc.register((lambda a,b,c: c.find(":VERSION" == 0)), func_version)

irc.internalRegister(onQuit, "onQuit")
irc.internalRegister(onConnect, "onConnect")

#Section 3: Main loop

chars = readChars()
hp = readHP()



irc.connect(network, port)
botThread = threading.Thread(target=irc.start)
botThread.start()
#listen()
#os.kill(os.getpid(), signal.SIGUSR1)
debug(30, sys._getframe())

# This stuff will only run if the bot quits:



	
