# generators for check functions

def simpleCheck(command):
	return (lambda sender, args, txt: command == txt.split()[0])
def masterCheck(command):
	return (lambda sender, args, txt: (command == txt.split()[0]) & (sender == irc.master))
	
