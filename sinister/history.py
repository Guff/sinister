class History(object):
    def __init__(self, state):
        self.position = 0
        self.states = []
        
        self.append(state)
    
    def append(self, state):
        if self.position < len(self.states):
            del self.states[self.position + 1:]
        
        self.states.append(state)
        self.position += 1
    
    def undo(self):
        self.position -= 1
        return self.states[self.position]
    
    def redo(self):
        self.position += 1
        return self.states[self.position]
