class CommandInterface(object):
    triggers = []
    acceptedTypes = ['PRIVMSG']
    help = '<no help defined (yet)>'
    
    def __init__(self):
        self.onStart()

    def onStart(self):
        pass

    def shouldExecute(self, message):
        if message.Type not in self.acceptedTypes:
            return False
        if message.Command.lower() not in self.triggers:
            return False
        
        return True

    def execute(self, message):
        pass
