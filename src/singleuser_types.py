from state import Agent
from state import movement
import random

#Keys for the controlling the pacman by the user
class keyboard_agent(Agent):
    # NOTE: Arrow keys also work.
    WEST_KEY  = 'a'
    EAST_KEY  = 'd'
    NORTH_KEY = 'w'
    SOUTH_KEY = 's'
    STOP_KEY = 'q'

    def __init__( self, index = 0 ):

        self.last_move = movement.STOP
        self.index = index
        self.keys = []

    def getAction( self, state):
        from gamegraphics import keys_waiting
        from gamegraphics import keys_pressed
        keys = list(keys_waiting()) + list(keys_pressed())
        if keys != []:
            self.keys = keys

        legal = state.get_legal_moves(self.index)
        move = self.getMove(legal)

        if move == movement.STOP:
            if self.last_move in legal:
                move = self.last_move

        if (self.STOP_KEY in self.keys) and movement.STOP in legal: move = movement.STOP

        if move not in legal:
            move = random.choice(legal)

        self.last_move = move
        return move

    def getMove(self, legal):
        move = movement.STOP
        if(self.WEST_KEY in self.keys or 'Left' in self.keys) and movement.left in legal:  move = movement.left
        if(self.EAST_KEY in self.keys or 'Right' in self.keys) and movement.right in legal: move = movement.right
        if(self.NORTH_KEY in self.keys or 'Up' in self.keys) and movement.up in legal:   move = movement.up
        if(self.SOUTH_KEY in self.keys or 'Down' in self.keys) and movement.down in legal: move = movement.down
        return move

class KeyboardAgent2(keyboard_agent):
    WEST_KEY  = 'j'
    EAST_KEY  = "l"
    NORTH_KEY = 'i'
    SOUTH_KEY = 'k'
    STOP_KEY = 'u'

    def getMove(self, legal):
        move = movement.STOP
        if   (self.WEST_KEY in self.keys) and movement.left in legal:  move = movement.left
        if   (self.EAST_KEY in self.keys) and movement.right in legal: move = movement.right
        if   (self.NORTH_KEY in self.keys) and movement.up in legal:   move = movement.up
        if   (self.SOUTH_KEY in self.keys) and movement.down in legal: move = movement.down
        return move
