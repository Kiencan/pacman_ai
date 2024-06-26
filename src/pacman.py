from state import game_state_data
from state import movement
from state import Actions
from gameflow import *
from utility_functions import nearest_cord
from utility_functions import coords_distance
import utility_functions, maze
import sys, types, time, random, os

import removegraphics
import gamedisplay

from optparse import OptionParser
import __main__

class game_state: #has accessor methods for accessing variables of game_state_data object
    explored = set() #keeps track of which states have had get_legal_moves called

    def getAndResetExplored():
        tmp = game_state.explored.copy()
        game_state.explored = set()
        return tmp
    getAndResetExplored = staticmethod(getAndResetExplored)

    def get_legal_moves( self, agent_index=0 ): #can help in assessing the actions that will help maximize or mimimize agents chances of winning
        if self.pac_won() or self.pac_lost(): return [] #we can have no legal actions for terminal state

        if agent_index == 0: #if it is pacman then
            return pac_rules.get_legal_moves( self ) #getting the legal actions for the PACMAN
        else:
            return ghost_rules.get_legal_moves( self, agent_index ) #getting the legal actions for the Ghost

    def produce_successor( self, agent_index, action): #Returns the successor game state after an agent takes an action (predicted game_state)
        #checking that action can be applied or not
        if self.pac_won() or self.pac_lost(): raise Exception('Can\'t generate a successor of a terminal state.')

        #copying the current state
        state = game_state(self)

        if agent_index == 0: #if the agent is Pacman then...
            state.data._eaten = [False for i in range(state.get_num_agents())] #maintains which agent has been eaten. In case of pacman, only the ghosts will be set to true if eaten
            pac_rules.apply_action( state, action ) #apply the action on the pacman
        else:
            ghost_rules.apply_action( state, action, agent_index )

        #penalty being incurred per unit time
        if agent_index == 0:
            state.data.score_change += -PENALTY # decreasing score on wasting time
        else:
            ghost_rules.dec_timer( state.data.agent_states[agent_index] ) #the timer for the ghost's scared state to finish

        #checking whehter
        ghost_rules.check_collid( state, agent_index ) #checks pacman's death

        #setting which agent has moved and the score state
        state.data.agent_moved = agent_index
        state.data.score += state.data.score_change
        #adding the state to already explored state
        game_state.explored.add(self)
        game_state.explored.add(state)
        return state

    def get_legal_pac_moves(self):
        return self.get_legal_moves(0)
    
    def produce_pac_successor( self, action ):
        return self.produce_successor(0, action ) #applying the action on the pacman
    
    def get_pac_state( self ):
        #returns the current state of Pacman (coord, direction)
        return self.data.agent_states[0].copy()

    def get_pacman_coord( self ):
        return self.data.agent_states[0].get_coord() #return the pacman's current position

    def get_ghost_states( self ):
        return self.data.agent_states[1:] #getting the states for all the ghosts

    def get_ghost_state( self, agent_index ):
        if agent_index == 0 or agent_index >= self.get_num_agents():
            raise Exception("Invalid index passed to get_ghost_state")
        return self.data.agent_states[agent_index]

    def get_ghost_coord( self, agent_index ):
        if agent_index == 0:
            raise Exception("Pacman's index passed to get_ghost_coord")
        return self.data.agent_states[agent_index].get_coord()
    
    def get_ghost_coords(self):
        return [s.get_coord() for s in self.get_ghost_states()]
    
    def get_num_agents( self ):
        return len(self.data.agent_states)

    def get_score( self ):
        return float(self.data.score)

    def get_big_coin(self):
        return self.data.big_coin #returning the remaining bigcoin positions
    
    def remaining_coin( self ):
        return self.data.coin.count() #getting the remaining coin on the maze

    def get_coin(self):
        return self.data.coin #return a 2d array of boolean indicating presence of coin on each location
    
    def get_walls(self):
        return self.data.maze.walls
    
    def has_coin(self, x, y):
        return self.data.coin[x][y]

    def has_wall(self, x, y):
        return self.data.maze.walls[x][y]

    def pac_lost( self ):
        return self.data._lose

    def pac_won( self ):
        return self.data._win

    def __init__( self, prevState = None ):
        if prevState != None: # Initial state
            self.data = game_state_data(prevState.data)
        else:
            self.data = game_state_data()

    def deep_copy( self ): #allowing for deep copy of the data attribute of the game_state
        state = game_state( self )
        state.data = self.data.deep_copy()
        return state
    
    def __eq__(self, other):
        return hasattr(other, 'data') and self.data == other.data

    def __hash__(self):
        return hash(self.data)

    def __str__(self):
        return str(self.data)

    def initialize( self, maze, numghost_agents=1000):
        self.data.initialize(maze, numghost_agents) #used to create the initial maze of the maze

SCARED_TIME = 40    # time till which ghosts are scared
KILL_DISTANCE = 0.7 # How close ghosts must be to Pacman to kill
PENALTY = 1 # Number of points lost when pacman not eating coin

class classic_rule:
    def __init__(self, timeout=30):
        self.timeout = timeout

    def newGame( self, maze, pacmanAgent, ghostAgents, display, no_display = False, catchExceptions=False):
        #taking all the state values for the new game
        agents = [pacmanAgent] + ghostAgents[:maze.get_ghosts_count()]
        initState = game_state()
        initState.initialize(maze, len(ghostAgents))
        game = Game(agents, display, self, catchExceptions=catchExceptions)
        game.state = initState
        self.initialState = initState.deep_copy()
        self.no_display = no_display
        return game

    def process(self, state, game): #checking whether game state is a win or a loss
        if state.pac_won(): self.win(state, game)
        if state.pac_lost(): self.lose(state, game)

    def win( self, state, game ): #printing win
        if not self.no_display:
            print("Bạn đã chiến thắng!")
            print("Điểm: " + str(state.data.score))
        game.gameOver = True

    def lose( self, state, game ): # printing loss
        if not self.no_display:
            print("Bạn đã thua!")
            print("Điểm:" + str(state.data.score))
        game.gameOver = True

    def get_progress(self, game): #returning how much coin eaten from the start
        return float(game.state.remaining_coin()) / self.initialState.remaining_coin()

    def agent_crash(self, game, agent_index):
        if agent_index == 0:
            print("Pacman crashed")
        else:
            print("A ghost crashed")

    def getMaxTotalTime(self, agentIndex):
        return self.timeout

    def getMaxStartupTime(self, agentIndex):
        return self.timeout

    def getMoveWarningTime(self, agentIndex):
        return self.timeout

    def getMoveTimeout(self, agentIndex):
        return self.timeout

    def getMaxTimeWarnings(self, agentIndex):
        return 0

class pac_rules:
    #functions for the pacman
    PACMAN_SPEED=1 #speed of the pacman has been set to one (same as that for the ghosts)

    def get_legal_moves( state ):
        return Actions.get_possible_moves( state.get_pac_state().location, state.data.maze.walls ) #returns the possible movement for pacman to move
    get_legal_moves = staticmethod( get_legal_moves )

    def apply_action( state, action ): # applying the action received on the pacman
        legal = pac_rules.get_legal_moves( state )
        if action not in legal:
            raise Exception("Illegal action " + str(action))
        pacman_state = state.data.agent_states[0]
        vector = Actions.direction_from_vector( action, pac_rules.PACMAN_SPEED ) #updating the pacman location
        pacman_state.location = pacman_state.location.produce_successor( vector )
        #eating coin
        next = pacman_state.location.get_coord()
        nearest = nearest_cord( next )
        if coords_distance( nearest, next ) <= 0.5 :#remove the coin when eaten
            pac_rules.eat( nearest, state )
    apply_action = staticmethod( apply_action )

    def eat( position, state ):
        x,y = position
        if state.data.coin[x][y]: #consuming the coin
            state.data.score_change += 10 #incrementing the score on consuming
            state.data.coin = state.data.coin.copy()
            state.data.coin[x][y] = False #the item is now removed from its position
            state.data.coin_eaten = position
            #checking whether all the coin has been eaten or not
            numcoin = state.remaining_coin()
            if numcoin == 0 and not state.data._lose:
                state.data.score_change += 500
                state.data._win = True
        #eating the bcoin
        if( position in state.get_big_coin() ): #now all ghost agents are eatable
            state.data.big_coin.remove( position )
            state.data.big_food_Eaten = position
            #Reset all ghosts' scared timers
            for index in range(1, len( state.data.agent_states)):
                state.data.agent_states[index].scared_timer = SCARED_TIME #all the ghosts are now in scared mode once the coin has been eaten
    eat = staticmethod( eat )

class ghost_rules:
    #functions for the ghost interacting with the enviroment
    GHOST_SPEED=1.0 # speed of ghost and pacman is same
    def get_legal_moves( state, ghostIndex ): #getting the legal_move for the ghost
        conf = state.get_ghost_state( ghostIndex ).location
        possible_moves = Actions.get_possible_moves( conf, state.data.maze.walls )
        reverse = Actions.reverse_dir( conf.direction )
        if movement.STOP in possible_moves:
            possible_moves.remove( movement.STOP ) #the ghost should not stop
        if reverse in possible_moves and len( possible_moves ) > 1: #if there is any other legal action except reversing the direction then remove reverse (cannot remove until dead end)
            possible_moves.remove( reverse )
        return possible_moves
    get_legal_moves = staticmethod( get_legal_moves )

    def apply_action( state, action, ghostIndex): #applying the action by getting the legal_move possible

        legal = ghost_rules.get_legal_moves( state, ghostIndex )
        if action not in legal:
            raise Exception("Illegal ghost action " + str(action))

        ghost_state = state.data.agent_states[ghostIndex]
        speed = ghost_rules.GHOST_SPEED
        if ghost_state.scared_timer > 0: speed /= 2.0 #decreasing the speed of the ghost in scared state
        vector = Actions.direction_from_vector( action, speed )
        ghost_state.location = ghost_state.location.produce_successor( vector ) #applying the action to the ghost_state
    apply_action = staticmethod( apply_action )

    def dec_timer( ghost_state): #this will decrerement the timer for the ghost being scared
        timer = ghost_state.scared_timer
        if timer == 1:
            ghost_state.location.coord = nearest_cord( ghost_state.location.coord )
        ghost_state.scared_timer = max( 0, timer - 1 ) #the timer cannot be below zero
    dec_timer = staticmethod( dec_timer )

    def check_collid( state, agent_index): #checking whether the pacman and the ghost has collided or not
        pacman_position = state.get_pacman_coord()
        if agent_index == 0: # Pacman just moved; Anyone can kill him
            for index in range( 1, len( state.data.agent_states ) ): #checking pacman has been killed by which ghost hence using a loop to check
                ghost_state = state.data.agent_states[index]
                ghost_coordinates = ghost_state.location.get_coord()
                if ghost_rules.can_kill( pacman_position, ghost_coordinates ):
                    ghost_rules.collide( state, ghost_state, index )
        else:
            ghost_state = state.data.agent_states[agent_index]
            ghost_coordinates = ghost_state.location.get_coord()
            if ghost_rules.can_kill( pacman_position, ghost_coordinates ):
                ghost_rules.collide( state, ghost_state, agent_index ) # setting the index of the ghost that killed the pacman
    check_collid = staticmethod( check_collid )

    def collide( state, ghost_state, agent_index): #sets the state on collision of pacman and the ghost
        if ghost_state.scared_timer > 0: #if the ghost is scared and still collides
            state.data.score_change += 200
            ghost_rules.put_ghost(state, ghost_state)
            ghost_state.scared_timer = 0
            # Added for first-person
            state.data._eaten[agent_index] = True # the agent is now eaten
        else:
            if not state.data._win:
                state.data.score_change -= 500
                state.data._lose = True #the game is lost as pacman is eaten
    collide = staticmethod( collide )

    def can_kill( pacman_position, ghost_coordinates ):
        #ghost and pacman distance is less that than the tolerance defined than its a kill
        return coords_distance( ghost_coordinates, pacman_position ) <= KILL_DISTANCE
    can_kill = staticmethod( can_kill )

    def put_ghost(state, ghost_state): #placing ghost agents at their proper positions
        ghost_state.location = ghost_state.start
    put_ghost = staticmethod( put_ghost )

#STARTING THE GAME
def default(str):
    return str + ' [Default: %default]'

def parse_agent_arguments(str):
    if str == None: return {}
    pieces = str.split(',')
    opts = {}
    for p in pieces:
        if '=' in p:
            key, val = p.split('=')
        else:
            key,val = p, 1
        opts[key] = val
    return opts

def parse_command( argv ):
    usageStr = """
    USAGE:      python pacman.py <options>
    EXAMPLES:   (1) python pacman.py
                    - starts an interactive game
                (2) python pacman.py --layout smallClassic --zoom 2
                OR  python pacman.py -l smallClassic -z 2
                    - starts an interactive game on a smaller board, zoomed in
    """

    p = OptionParser(usageStr)

    #ADDING THE PARSING OPTIONS
    p.add_option('-n', '--numGames', dest='numGames', type='int',
                      help=default('the number of GAMES to play'), metavar='GAMES', default=1)
    p.add_option('-l', '--maze', dest='maze',
                      help=default('the LAYOUT_FILE from which to load the map maze'),
                      metavar='LAYOUT_FILE', default='originalClassic')
    p.add_option('-p', '--pacman', dest='pacman',
                      help=default('the agent TYPE in the pacmanAgents module to use'),
                      metavar='TYPE', default='keyboard_agent')
    p.add_option('-t', '--textGraphics', action='store_true', dest='textGraphics',
                      help='Display output as text only', default=False)
    p.add_option('-q', '--no_displayTextGraphics', action='store_true', dest='no_displayGraphics',
                      help='Generate minimal output and no graphics', default=False)
    p.add_option('-g', '--ghosts', dest='ghost',
                      help=default('the ghost agent TYPE in the ghostAgents module to use'),
                      metavar = 'TYPE', default='random_ghost')
    p.add_option('-k', '--ghosts_count', type='int', dest='ghosts_count',
                      help=default('The maximum number of ghosts to use'), default=4)
    p.add_option('-z', '--zoom', type='float', dest='zoom',
                      help=default('Zoom the size of the graphics window'), default=1.0)
    p.add_option('-f', '--fixRandomSeed', action='store_true', dest='fixRandomSeed',
                      help='Fixes the random seed to always play the same game', default=False)
    p.add_option('-r', '--recordActions', action='store_true', dest='record',
                      help='Writes game histories to a file (named by the time they were played)', default=False)
    p.add_option('--replay', dest='gameToReplay',
                      help='A recorded game file (pickle) to replay', default=None)
    p.add_option('-a','--agentArgs',dest='agentArgs',
                      help='Comma separated values sent to agent. e.g. "opt1=val1,opt2,opt3=val3"')
    p.add_option('-x', '--numTraining', dest='numTraining', type='int',
                      help=default('How many episodes are training (suppresses output)'), default=0)
    p.add_option('--frame_t', dest='frame_t', type='float',
                      help=default('Time to delay between frames; <0 means keyboard'), default=0.1)
    p.add_option('-c', '--catchExceptions', action='store_true', dest='catchExceptions',
                      help='Turns on exception handling and timeouts during games', default=False)
    p.add_option('--timeout', dest='timeout', type='int',
                      help=default('Maximum length of time an agent can spend computing in a single game'), default=30)

    options, otherjunk = p.parse_args(argv)
    #error command generated
    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    arguments = dict()

    if options.fixRandomSeed:
        random.seed('pacman')

    #setting the maze
    arguments['maze'] = maze.get_layout(options.maze)
    if arguments['maze'] == None: raise Exception("The maze " + options.maze + " cannot be found") #in case of the maze not being found

    # Choose a Pacman agent
    # noKeyboard = False
    noKeyboard = options.gameToReplay == None and (options.textGraphics or options.no_displayGraphics)
    pacmanType = load_agent(options.pacman, noKeyboard)
    agentOpts = parse_agent_arguments(options.agentArgs)
    if options.numTraining > 0:
        arguments['numTraining'] = options.numTraining
        if 'numTraining' not in agentOpts:
            agentOpts['numTraining'] = options.numTraining
    pacman = pacmanType(**agentOpts) # Instantiate Pacman with agentArgs
    arguments['pacman'] = pacman

    if 'numTrain' in agentOpts:
        options.numQuiet = int(agentOpts['numTrain'])
        options.numIgnore = int(agentOpts['numTrain'])

    # Choose a ghost agent
    ghostType = load_agent(options.ghost, noKeyboard)
    arguments['ghosts'] = [ghostType( i+1 ) for i in range( options.ghosts_count )]

    # Choose a display format
    if options.no_displayGraphics:
        arguments['display'] = removegraphics.null_graphic()
    elif options.textGraphics:
        removegraphics.SLEEP_TIME = options.frame_t
        arguments['display'] = removegraphics.PacmanGraphics()
    else:
        arguments['display'] = gamedisplay.pac_graphic(options.zoom, frame_t = options.frame_t)
    arguments['numGames'] = options.numGames
    arguments['record'] = options.record
    arguments['catchExceptions'] = options.catchExceptions
    arguments['timeout'] = options.timeout

    if options.gameToReplay != None:
        print('Replaying recorded game %s.' % options.gameToReplay)
        import pickle
        f = open(options.gameToReplay, 'rb')
        try:
            recorded = pickle.load(f)
        finally:
            f.close()
        recorded['display'] = arguments['display']
        replayGame(**recorded)
        sys.exit(0)

    return arguments

#utility function used for loading module in which agent is defined
def load_agent(pacman, nographics):
    pythonPathStr = os.path.expandvars("$PYTHONPATH")
    if pythonPathStr.find(';') == -1:
        pythonPathDirs = pythonPathStr.split(':')
    else:
        pythonPathDirs = pythonPathStr.split(';')
    pythonPathDirs.append('.')

    for moduleDir in pythonPathDirs:
        if not os.path.isdir(moduleDir): continue
        moduleNames = [f for f in os.listdir(moduleDir) if f.endswith('ypes.py')]
        for modulename in moduleNames:
            try:
                module = __import__(modulename[:-3])
            except ImportError:
                continue
            if pacman in dir(module):
                if nographics and modulename == 'singleuser_types.py':
                    raise Exception('Using the keyboard requires graphics (not text display)')
                return getattr(module, pacman)

    raise Exception('The agent ' + pacman + ' is not specified in any *Agents.py.')

def replayGame(maze, actions, display):
    import pacman_types
    import ghost_types
    rules = classic_rule()
    agents = [pacman_types.GreedyAgent()] + [ghost_types.random_ghost(i+1)
                                             for i in range(maze.get_ghosts_count())]
    game = rules.newGame(maze, agents[0], agents[1:], display)
    state = game.state
    display.initialize(state.data)

    for action in actions:
            # Execute the action
        state = state.produce_successor(*action)
        # Change the display
        display.update(state.data)
        # Allow for game specific conditions (winning, losing, etc.)
        rules.process(state, game)

    display.finish()

def initiate_pacman(maze, pacman, ghosts, display, numGames, record, numTraining=0, catchExceptions=False, timeout=30):
    __main__.__dict__['_display'] = display
    global scores

    rules = classic_rule(timeout)
    games = []

    for i in range( numGames ):
        beQuiet = i < numTraining
        if beQuiet:
                # Suppress output and graphics
            gameDisplay = removegraphics.null_graphic()
            rules.no_display = True
        else:
            gameDisplay = display
            rules.no_display = False
        game = rules.newGame(maze, pacman, ghosts, gameDisplay, beQuiet, catchExceptions)
        game.run()
        if not beQuiet: 
            games.append(game)

        if record:
            import time
            import pickle
            fname = ('recorded-game-%d' % (i + 1)) + '-'.join([str(t) for t in time.localtime()[1:6]])
            f = open(fname, 'wb')
            components = {'maze': maze, 'actions': game.moveHistory}
            pickle.dump(components, f)
            f.close()

    if (numGames - numTraining) > 0:
        scores = [game.state.get_score() for game in games]
        wins = [game.state.pac_won() for game in games]
        winRate = wins.count(True)/ float(len(wins))

        average_wins = []
        CapCount = 0
        for game in games:
            if game.state.pac_won():
                average_wins.append(game.state.get_score())
            if len(game.state.get_big_coin())==0:
                CapCount += 1
        # print('%d game thắng trên tổng số %d game ---> Tỉ lệ thắng: %.2f' % (wins.count(True), len(wins), winRate*100))
        # print('Điểm trung bình: ', sum(scores) / float(len(scores)))
        print('%d game thắng trên tổng số %d game ---> Tỉ lệ thắng: %.2f' % (wins.count(True), len(wins), winRate*100))
        print('Điểm trung bình: '+str(sum(scores) / float(len(scores))))
        # print('Average Score:', sum(scores) / float(len(scores)))
        # print('Scores:       ', ', '.join([str(score) for score in scores]))
        # print('Win Rate:      %d/%d (%.2f)' %
        #       (wins.count(True), len(wins), winRate))
        # print('Record:       ', ', '.join(
        #     [['Loss', 'Win'][int(w)] for w in wins]))

    return games

if __name__ == '__main__':
    arguments = parse_command(sys.argv[1:]) # Get game components based on input
    initiate_pacman(**arguments)
    pass
