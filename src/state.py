from utility_functions import *
import time, os
import traceback
import sys
# from gameflow import *

class Agent:
    #returns the index of the agent if any.
    def __init__(self, index=0):
        self.index = index

    def getAction(self, state):
        raiseNotDefined()

class movement:
    #Strings defined for the direction (POLES)
    up = 'up'
    down = 'down'
    right = 'right'
    left = 'left'
    STOP = 'Stop'

    #In case, pacman is going in a certain direction, its poles relative to it are defined below:
    left_dir = {up: left, down: right, right:  up, left:  down, STOP:  STOP}
    right_dir = dict([(y,x) for x, y in list(left_dir.items())]) #right is the reverse of left
    reverse_dir = {up: down, down: up, right: left, left: right, STOP: STOP}

class location:
#takes in the initial position of the Pacman and its initial direction as the argument
    def __init__(self, coord, direction):
        self.coord = coord #coords
        self.direction = direction #direction of movement

    #UTILITY FUNCTIONS
    def get_coord(self):
        return (self.coord)

    def get_dir(self):
        return self.direction

    def isInteger(self):
        x,y = self.coord
        return x == int(x) and y == int(y)
    
    def __eq__(self, other):
        if other == None: return False
        return (self.coord == other.coord and self.direction == other.direction)

    def __hash__(self):
        x = hash(self.coord)
        y = hash(self.direction)
        return hash(x + 13 * y)

    def __str__(self):
        return "(x,y)="+str(self.coord)+", "+str(self.direction)

    #converts position to direction vector to implement position on the pacman graph
    def produce_successor(self, vector):

        x, y= self.coord
        dx, dy = vector
        direction = Actions.vec_to_dir(vector)
        if direction == movement.STOP:
            direction = self.direction # There is no stop direction
        return location((x + dx, y+dy), direction)

class AgentState:

    #agent_states hold the state of an agent (location, speed, scared, etc).
    def __init__( self, startLocation, is_pac):
        self.start = startLocation
        self.location = startLocation
        self.is_pac = is_pac #is the agent Pacman or ghost?
        self.scared_timer = 0 #time until the ghost can be eaten
        self.numCarrying = 0
        self.numReturned = 0

    def __str__( self ):
        if self.is_pac:
            return "Pacman: " + str(self.location)
        else:
            return "Ghost: " + str(self.location)

    def __eq__(self, other):
        if other == None:
            return False
        return self.location == other.location and self.scared_timer == other.scared_timer

    def __hash__(self):
        return hash(hash(self.location) + 13 * hash(self.scared_timer))

    def copy(self):
        state = AgentState(self.start, self.is_pac)
        state.location = self.location
        state.scared_timer = self.scared_timer #time until which the agent would be eatable
        state.numCarrying = self.numCarrying
        state.numReturned = self.numReturned
        return state

    #UTILITY FUNCTIONS
    def get_coord(self):
        if self.location == None: return None
        return self.location.get_coord()

    def get_dir(self):
        return self.location.get_dir()

class Grid:

    def __init__(self, width, height, initialValue=False, bitRepresentation=None):
        if initialValue not in [False, True]: raise Exception('Grids can only contain booleans')
        self.CELLS_PER_INT = 30 #cells per pixel
        #dimensions of the maze
        self.width = width
        self.height = height
        self.data = [[initialValue for y in range(height)] for x in range(width)] #initializing array for the maze
        if bitRepresentation:
            self.unpack_bits(bitRepresentation)

    def __getitem__(self, i):
        return self.data[i]

    def __setitem__(self, key, item):
        self.data[key] = item

    def __str__(self):
        out = [[str(self.data[x][y])[0] for x in range(self.width)] for y in range(self.height)]
        out.reverse()
        return '\n'.join([''.join(x) for x in out])

    def __eq__(self, other):
        if other == None: return False
        return self.data == other.data

    def __hash__(self):
        # return hash(str(self))
        base = 1
        h = 0
        for l in self.data:
            for i in l:
                if i:
                    h += base
                base *= 2
        return hash(h)

    def copy(self): #returns a copy of the grid (deep_copy)
        g = Grid(self.width, self.height)
        g.data = [x[:] for x in self.data]
        return g

    def deep_copy(self):
        return self.copy()

    def shallow_copy(self): #pointers to the grid passed
        g = Grid(self.width, self.height)
        g.data = self.data
        return g

    def count(self, item =True ): #returns number of items in the data
        return sum([x.count(item) for x in self.data])

    def as_list(self, key = True): #return the Grid as a list
        list = []
        for x in range(self.width):
            for y in range(self.height):
                if self[x][y] == key: list.append( (x,y) )
        return list
    
    def packBits(self):
        bits = [self.width, self.height]
        currentInt = 0
        for i in range(self.height * self.width):
            bit = self.CELLS_PER_INT - (i % self.CELLS_PER_INT) - 1
            x, y = self.cell_index_to_coord(i)
            if self[x][y]:
                currentInt += 2 ** bit
            if (i + 1) % self.CELLS_PER_INT == 0:
                bits.append(currentInt)
                currentInt = 0
        bits.append(currentInt)
        return tuple(bits)

    def cell_index_to_coord(self, index):
        x = index // self.height
        y = index % self.height
        return x, y

    def unpack_bits(self, bits):
        cell = 0
        for packed in bits:
            for bit in self.unpack_int(packed, self.CELLS_PER_INT):
                if cell == self.width * self.height: break
                x, y = self.cell_index_to_coord(cell)
                self[x][y] = bit
                cell += 1

    def unpack_int(self, packed, size):
        flag = []
        if packed < 0: raise ValueError("must be a positive integer")
        for i in range(size):
            n = 2 ** (self.CELLS_PER_INT - i - 1)
            if packed >= n:
                flag.append(True)
                packed -= n
            else:
                flag.append(False)
        return flag

def reconstituteGrid(bitRep):
    if type(bitRep) is not type((1,2)):
        return bitRep
    width, height = bitRep[:2]
    return Grid(width, height, bitRepresentation=bitRep[2:])


class Actions:
    # movement
    _directions = {movement.up: (0, 1),
                   movement.down: (0, -1),
                   movement.right:  (1, 0),
                   movement.left:  (-1, 0),
                   movement.STOP:  (0, 0)}

    directions_as_list = list(_directions.items())

    TOLERANCE = .001 #for transition of pacman between the grids

    def reverse_dir(action):
        if action == movement.up:
            return movement.down
        if action == movement.down:
            return movement.up
        if action == movement.right:
            return movement.left
        if action == movement.left:
            return movement.right
        return action
    reverse_dir = staticmethod(reverse_dir)

    def vec_to_dir(vector):
        dx, dy = vector
        if dy > 0:
            return movement.up
        if dy < 0:
            return movement.down
        if dx < 0:
            return movement.left
        if dx > 0:
            return movement.right
        return movement.STOP
    vec_to_dir = staticmethod(vec_to_dir)

   #returning the direction as a vector, incorporated with the speed
    def direction_from_vector(direction, speed = 1.0):
        dx, dy =  Actions._directions[direction]
        return (dx * speed, dy * speed)
    direction_from_vector = staticmethod(direction_from_vector)

    #location is the current game_state of an agent
    def get_possible_moves(location, walls):
        possible = [] #initialized empty
        x, y = location.coord #gets the current coord of Pacman
        x_int, y_int = int(x + 0.5), int(y + 0.5)

        # In between grid points, all agents must continue straight
        if (abs(x - x_int) + abs(y - y_int)  > Actions.TOLERANCE):
            return [location.get_dir()]

        for dir, vec in Actions.directions_as_list:
            dx, dy = vec
            next_y = y_int + dy
            next_x = x_int + dx
            #if the coords are not of the walls, then append to possible
            if not walls[next_x][next_y]: possible.append(dir)

        return possible

    get_possible_moves = staticmethod(get_possible_moves)

    def getLegalNeighbors(position, walls):
        x,y = position
        x_int, y_int = int(x + 0.5), int(y + 0.5)
        neighbors = []
        for dir, vec in Actions.directions_as_list:
            dx, dy = vec
            next_x = x_int + dx
            if next_x < 0 or next_x == walls.width: continue
            next_y = y_int + dy
            if next_y < 0 or next_y == walls.height: continue
            if not walls[next_x][next_y]: neighbors.append((next_x, next_y))
        return neighbors
    getLegalNeighbors = staticmethod(getLegalNeighbors)

    def getSuccessor(position, action):
        dx, dy = Actions.direction_from_vector(action)
        x, y = position
        return (x + dx, y + dy)
    getSuccessor = staticmethod(getSuccessor)

class game_state_data: #data pertaining to each state of the game

    def __init__( self, prevState = None ):
        if prevState != None:
            #MAINTAINING THE PREVIOUS STATE IN ORDER TO COMPARE
            self.coin = prevState.coin.shallow_copy()
            self.big_coin = prevState.big_coin[:]
            self.agent_states = self.copy_agent_states( prevState.agent_states )
            self.maze = prevState.maze #previous maze maze
            self._eaten = prevState._eaten
            self.score = prevState.score

        #MAINTAINING STATES FOR THE AGENT
        self.coin_eaten = None
        self._coinAdded = None
        self.big_food_Eaten = None
        self.agent_moved = None #checking if the agent has moved from previous position
        self._lose = False #game lost
        self._win = False #game won
        self.score_change = 0

    def deep_copy(self): #DEEP COPYING
        state = game_state_data(self)
        state.coin = self.coin.deep_copy()
        state.maze = self.maze.deep_copy()
        state.agent_moved = self.agent_moved
        state.coin_eaten = self.coin_eaten
        state._coinAdded = self._coinAdded
        state.big_food_Eaten = self.big_food_Eaten
        return state

    def copy_agent_states( self, agent_states ):
        copied_states = []
        for agent_state in agent_states:
            copied_states.append(agent_state.copy())
        return copied_states
    
    def __eq__( self, other ):
        """
        Allows two states to be compared.
        """
        if other == None: return False
        # TODO Check for type of other
        if not self.agent_states == other.agent_states: return False
        if not self.coin == other.coin: return False
        if not self.big_coin == other.big_coin: return False
        if not self.score == other.score: return False
        return True

    def __hash__( self ):
        """
        Allows states to be keys of dictionaries.
        """
        for i, state in enumerate(self.agent_states):
            try:
                int(hash(state))
            except TypeError as e:
                print(e)
                #hash(state)
        return int((hash(tuple(self.agent_states)) + 13*hash(self.coin) + 113* hash(tuple(self.big_coin)) + 7 * hash(self.score)) % 1048575 )

    def __str__( self ):
        width, height = self.maze.width, self.maze.height
        map = Grid(width, height)
        if type(self.coin) == type((1,2)):
            self.coin = reconstituteGrid(self.coin)
        for x in range(width):
            for y in range(height):
                coin, walls = self.coin, self.layout.walls
                map[x][y] = self._foodWallStr(coin[x][y], walls[x][y])

        for agent_state in self.agent_states:
            if agent_state == None: continue
            if agent_state.location == None: continue
            x,y = [int( i ) for i in nearest_cord(agent_state.location.coord)]
            agent_dir = agent_state.location.direction
            if agent_state.is_pac:
                map[x][y] = self._pacStr(agent_dir)
            else:
                map[x][y] = self._ghostStr(agent_dir)

        for x, y in self.big_coin:
            map[x][y] = 'o'

        return str(map) + ("\Điểm: %d\n" % self.score)

    def _foodWallStr( self, has_coin, has_wall ):
        if has_coin:
            return '.'
        elif has_wall:
            return '%'
        else:
            return ' '

    def _pacStr( self, dir ):
        if dir == movement.up:
            return 'v'
        if dir == movement.down:
            return '^'
        if dir == movement.left:
            return '>'
        return '<'

    def _ghostStr(self, dir):
        return 'G'
        # if dir == movement.up:
        #     return 'M'
        # if dir == movement.down:
        #     return 'W'
        # if dir == movement.left:
        #     return '3'
        # return 'E'

    def initialize( self, maze, numghost_agents ):
        #creating the game_state from the maze (INITIAL STATE)
        self.coin = maze.coin.copy()
        #self.big_coin = []
        self.big_coin = maze.big_coin[:]
        self.maze = maze
        self.score = 0
        self.score_change = 0

        self.agent_states = []
        ghosts_count = 0
        for is_pac, coord in maze.agent_coord:
            if not is_pac:
                if ghosts_count == numghost_agents: continue # Max ghosts reached already
                else: ghosts_count += 1
            self.agent_states.append( AgentState( location( coord, movement.STOP), is_pac) )
        self._eaten = [False for a in self.agent_states] #Checking that agent is eaten or not (as pacman can eat the agents)


# class Game:
#     def __init__( self, agents, display, rules, startingIndex=0, muteAgents=False, catchExceptions=False):
#         self.agentCrashed = False
#         self.agents = agents
#         self.display = display
#         self.rules = rules
#         self.startingIndex = startingIndex
#         self.gameOver = False
#         self.muteAgents = muteAgents
#         self.catchExceptions = catchExceptions
#         self.moveHistory = []
#         self.totalAgentTimes = [0 for agent in agents]
#         self.totalAgentTimeWarnings = [0 for agent in agents]
#         self.agentTimeout = False
#         import io
#         self.agentOutput = [io.StringIO() for agent in agents]

#     def getProgress(self):
#         if self.gameOver:
#             return 1.0
#         else:
#             return self.rules.getProgress(self)

#     def _agentCrash( self, agentIndex, quiet=False):
#         "Helper method for handling agent crashes"
#         if not quiet: traceback.print_exc()
#         self.gameOver = True
#         self.agentCrashed = True
#         self.rules.agentCrash(self, agentIndex)

#     OLD_STDOUT = None
#     OLD_STDERR = None

#     def mute(self, agentIndex):
#         if not self.muteAgents: return
#         global OLD_STDOUT, OLD_STDERR
#         import io
#         OLD_STDOUT = sys.stdout
#         OLD_STDERR = sys.stderr
#         sys.stdout = self.agentOutput[agentIndex]
#         sys.stderr = self.agentOutput[agentIndex]

#     def unmute(self):
#         if not self.muteAgents: return
#         global OLD_STDOUT, OLD_STDERR
#         # Revert stdout/stderr to originals
#         sys.stdout = OLD_STDOUT
#         sys.stderr = OLD_STDERR


#     def run( self ):
#         """
#         Main control loop for game play.
#         """
#         self.display.initialize(self.state.data)
#         self.numMoves = 0

#         ###self.display.initialize(self.state.makeObservation(1).data)
#         # inform learning agents of the game start
#         for i in range(len(self.agents)):
#             agent = self.agents[i]
#             if not agent:
#                 self.mute(i)
#                 # this is a null agent, meaning it failed to load
#                 # the other team wins
#                 print("Agent %d failed to load" % i, file=sys.stderr)
#                 self.unmute()
#                 self._agentCrash(i, quiet=True)
#                 return
#             if ("registerInitialState" in dir(agent)):
#                 self.mute(i)
#                 if self.catchExceptions:
#                     try:
#                         timed_func = TimeoutFunction(agent.registerInitialState, int(self.rules.getMaxStartupTime(i)))
#                         try:
#                             start_time = time.time()
#                             timed_func(self.state.deep_copy())
#                             time_taken = time.time() - start_time
#                             self.totalAgentTimes[i] += time_taken
#                         except TimeoutFunctionException:
#                             print("Agent %d ran out of time on startup!" % i, file=sys.stderr)
#                             self.unmute()
#                             self.agentTimeout = True
#                             self._agentCrash(i, quiet=True)
#                             return
#                     except Exception as data:
#                         self._agentCrash(i, quiet=False)
#                         self.unmute()
#                         return
#                 else:
#                     agent.registerInitialState(self.state.deep_copy())
#                 ## TODO: could this exceed the total time
#                 self.unmute()

#         agentIndex = self.startingIndex
#         numAgents = len( self.agents )

#         while not self.gameOver:
#             # Fetch the next agent
#             agent = self.agents[agentIndex]
#             move_time = 0
#             skip_action = False
#             # Generate an observation of the state
#             if 'observationFunction' in dir( agent ):
#                 self.mute(agentIndex)
#                 if self.catchExceptions:
#                     try:
#                         timed_func = TimeoutFunction(agent.observationFunction, int(self.rules.getMoveTimeout(agentIndex)))
#                         try:
#                             start_time = time.time()
#                             observation = timed_func(self.state.deep_copy())
#                         except TimeoutFunctionException:
#                             skip_action = True
#                         move_time += time.time() - start_time
#                         self.unmute()
#                     except Exception as data:
#                         self._agentCrash(agentIndex, quiet=False)
#                         self.unmute()
#                         return
#                 else:
#                     observation = agent.observationFunction(self.state.deep_copy())
#                 self.unmute()
#             else:
#                 observation = self.state.deep_copy()

#             # Solicit an action
#             action = None
#             self.mute(agentIndex)
#             if self.catchExceptions:
#                 try:
#                     timed_func = TimeoutFunction(agent.getAction, int(self.rules.getMoveTimeout(agentIndex)) - int(move_time))
#                     try:
#                         start_time = time.time()
#                         if skip_action:
#                             raise TimeoutFunctionException()
#                         action = timed_func( observation )
#                     except TimeoutFunctionException:
#                         print("Agent %d timed out on a single move!" % agentIndex, file=sys.stderr)
#                         self.agentTimeout = True
#                         self._agentCrash(agentIndex, quiet=True)
#                         self.unmute()
#                         return

#                     move_time += time.time() - start_time

#                     if move_time > self.rules.getMoveWarningTime(agentIndex):
#                         self.totalAgentTimeWarnings[agentIndex] += 1
#                         print("Agent %d took too long to make a move! This is warning %d" % (agentIndex, self.totalAgentTimeWarnings[agentIndex]), file=sys.stderr)
#                         if self.totalAgentTimeWarnings[agentIndex] > self.rules.getMaxTimeWarnings(agentIndex):
#                             print("Agent %d exceeded the maximum number of warnings: %d" % (agentIndex, self.totalAgentTimeWarnings[agentIndex]), file=sys.stderr)
#                             self.agentTimeout = True
#                             self._agentCrash(agentIndex, quiet=True)
#                             self.unmute()
#                             return

#                     self.totalAgentTimes[agentIndex] += move_time
#                     #print("Agent: %d, time: %f, total: %f" % (agentIndex, move_time, self.totalAgentTimes[agentIndex]))
#                     if self.totalAgentTimes[agentIndex] > self.rules.getMaxTotalTime(agentIndex):
#                         print("Agent %d ran out of time! (time: %1.2f)" % (agentIndex, self.totalAgentTimes[agentIndex]), file=sys.stderr)
#                         self.agentTimeout = True
#                         self._agentCrash(agentIndex, quiet=True)
#                         self.unmute()
#                         return
#                     self.unmute()
#                 except Exception as data:
#                     self._agentCrash(agentIndex)
#                     self.unmute()
#                     return
#             else:
#                 action = agent.getAction(observation)
#             self.unmute()

#             # Execute the action
#             self.moveHistory.append( (agentIndex, action) )
#             if self.catchExceptions:
#                 try:
#                     self.state = self.state.produce_successor( agentIndex, action )
#                 except Exception as data:
#                     self.mute(agentIndex)
#                     self._agentCrash(agentIndex)
#                     self.unmute()
#                     return
#             else:
#                 self.state = self.state.produce_successor( agentIndex, action )

#             # Change the display
#             self.display.update( self.state.data )
#             ###idx = agentIndex - agentIndex % 2 + 1
#             ###self.display.update( self.state.makeObservation(idx).data )

#             # Allow for game specific conditions (winning, losing, etc.)
#             self.rules.process(self.state, self)
#             # Track progress
#             if agentIndex == numAgents + 1: self.numMoves += 1
#             # Next agent
#             agentIndex = ( agentIndex + 1 ) % numAgents

#             if _BOINC_ENABLED:
#                 boinc.set_fraction_done(self.getProgress())

#         # inform a learning agent of the game result
#         for agentIndex, agent in enumerate(self.agents):
#             if "final" in dir( agent ) :
#                 try:
#                     self.mute(agentIndex)
#                     agent.final( self.state )
#                     self.unmute()
#                 except Exception as data:
#                     if not self.catchExceptions: raise data
#                     self._agentCrash(agentIndex)
#                     self.unmute()
#                     return
#         self.display.finish()
