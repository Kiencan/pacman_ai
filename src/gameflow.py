from utility_functions import *
import time, os
import traceback
import sys

try:
    import boinc
    _BOINC_ENABLED = True
except:
    _BOINC_ENABLED = False

#PACMAN AGENT TYPE
REFLEX = "reflex_agent"
MINIMAX = "minimax_agent"
ALPHA = "alpha_beta_agent"
EXPECTIMAX = "expecti_max_agent"
SEARCH = "search_agent"

#maze
TEST = "testClassic"
MINI = "minimaxClassic"
SMALL = "smallClassic"
TRAPPED = "trappedClassic"
ORIGINAL = "originalClassic"
TRICKY = "trickyClassic"

# class Game:

#     # manages the control flow, requesting actions from agents.
#     def __init__( self, agents, display, rules, s_index=0):
#         self.agent_crash = False
#         self.agents = agents
#         self.display = display
#         self.rules = rules
#         self.s_index = s_index
#         self.game_finish = False
#         self.move_history = []
#         import io
#         self.agent_out = [io.StringIO() for agent in agents]

#     def get_progress(self): #Checking whether the game is over or not
#         if self.game_finish:
#             return 1.0
#         else:
#             return self.rules.get_progress(self)

#     def run( self ):
#         self.display.initialize(self.state.data)
#         self.numMoves = 0

#         # inform learning agents of the game start
#         for i in range(len(self.agents)):
#             agent = self.agents[i]
#             if ("registerInitialState" in dir(agent)):
#                 agent.registerInitialState(self.state.deep_copy())

#         agent_index = self.s_index
#         numAgents = len( self.agents )

#         while not self.game_finish:
#             # Fetch the next agent
#             agent = self.agents[agent_index]
#             move_time = 0
#             skip_action = False
#             # Generate an observation of the state
#             if 'observationFunction' in dir( agent ):
#                 observation = agent.observationFunction(self.state.deep_copy())
#             else:
#                 observation = self.state.deep_copy()

#             # Solicit an action
#             action = agent.get_move(observation)

#             # Execute the action
#             self.move_history.append( (agent_index, action) )
#             self.state = self.state.produce_successor( agent_index, action )

#             # Change the display
#             self.display.update( self.state.data )

#             # Allow for game specific conditions (winning, losing, etc.)
#             self.rules.process(self.state, self)
#             # Track progress
#             if agent_index == numAgents + 1: self.numMoves += 1
#             # Next agent
#             agent_index = ( agent_index + 1 ) % numAgents

#         self.display.finish()

class Game:
    def __init__( self, agents, display, rules, startingIndex=0, muteAgents=False, catchExceptions=False):
        self.agentCrashed = False
        self.agents = agents
        self.display = display
        self.rules = rules
        self.startingIndex = startingIndex
        self.gameOver = False
        self.muteAgents = muteAgents
        self.catchExceptions = catchExceptions
        self.moveHistory = []
        self.totalAgentTimes = [0 for agent in agents]
        self.totalAgentTimeWarnings = [0 for agent in agents]
        self.agentTimeout = False
        import io
        self.agentOutput = [io.StringIO() for agent in agents]

    def getProgress(self):
        if self.gameOver:
            return 1.0
        else:
            return self.rules.getProgress(self)

    def _agentCrash( self, agentIndex, quiet=False):
        "Helper method for handling agent crashes"
        if not quiet: traceback.print_exc()
        self.gameOver = True
        self.agentCrashed = True
        self.rules.agentCrash(self, agentIndex)

    OLD_STDOUT = None
    OLD_STDERR = None

    def mute(self, agentIndex):
        if not self.muteAgents: return
        global OLD_STDOUT, OLD_STDERR
        import io
        OLD_STDOUT = sys.stdout
        OLD_STDERR = sys.stderr
        sys.stdout = self.agentOutput[agentIndex]
        sys.stderr = self.agentOutput[agentIndex]

    def unmute(self):
        if not self.muteAgents: return
        global OLD_STDOUT, OLD_STDERR
        # Revert stdout/stderr to originals
        sys.stdout = OLD_STDOUT
        sys.stderr = OLD_STDERR


    def run( self ):
        """
        Main control loop for game play.
        """
        self.display.initialize(self.state.data)
        self.numMoves = 0

        ###self.display.initialize(self.state.makeObservation(1).data)
        # inform learning agents of the game start
        for i in range(len(self.agents)):
            agent = self.agents[i]
            if not agent:
                self.mute(i)
                # this is a null agent, meaning it failed to load
                # the other team wins
                print("Agent %d failed to load" % i, file=sys.stderr)
                self.unmute()
                self._agentCrash(i, quiet=True)
                return
            if ("registerInitialState" in dir(agent)):
                self.mute(i)
                if self.catchExceptions:
                    try:
                        timed_func = TimeoutFunction(agent.registerInitialState, int(self.rules.getMaxStartupTime(i)))
                        try:
                            start_time = time.time()
                            timed_func(self.state.deep_copy())
                            time_taken = time.time() - start_time
                            self.totalAgentTimes[i] += time_taken
                        except TimeoutFunctionException:
                            print("Agent %d ran out of time on startup!" % i, file=sys.stderr)
                            self.unmute()
                            self.agentTimeout = True
                            self._agentCrash(i, quiet=True)
                            return
                    except Exception as data:
                        self._agentCrash(i, quiet=False)
                        self.unmute()
                        return
                else:
                    agent.registerInitialState(self.state.deep_copy())
                ## TODO: could this exceed the total time
                self.unmute()

        agentIndex = self.startingIndex
        numAgents = len( self.agents )

        while not self.gameOver:
            # Fetch the next agent
            agent = self.agents[agentIndex]
            move_time = 0
            skip_action = False
            # Generate an observation of the state
            if 'observationFunction' in dir( agent ):
                self.mute(agentIndex)
                if self.catchExceptions:
                    try:
                        timed_func = TimeoutFunction(agent.observationFunction, int(self.rules.getMoveTimeout(agentIndex)))
                        try:
                            start_time = time.time()
                            observation = timed_func(self.state.deep_copy())
                        except TimeoutFunctionException:
                            skip_action = True
                        move_time += time.time() - start_time
                        self.unmute()
                    except Exception as data:
                        self._agentCrash(agentIndex, quiet=False)
                        self.unmute()
                        return
                else:
                    observation = agent.observationFunction(self.state.deep_copy())
                self.unmute()
            else:
                observation = self.state.deep_copy()

            # Solicit an action
            action = None
            self.mute(agentIndex)
            if self.catchExceptions:
                try:
                    timed_func = TimeoutFunction(agent.getAction, int(self.rules.getMoveTimeout(agentIndex)) - int(move_time))
                    try:
                        start_time = time.time()
                        if skip_action:
                            raise TimeoutFunctionException()
                        action = timed_func( observation )
                    except TimeoutFunctionException:
                        print("Agent %d timed out on a single move!" % agentIndex, file=sys.stderr)
                        self.agentTimeout = True
                        self._agentCrash(agentIndex, quiet=True)
                        self.unmute()
                        return

                    move_time += time.time() - start_time

                    if move_time > self.rules.getMoveWarningTime(agentIndex):
                        self.totalAgentTimeWarnings[agentIndex] += 1
                        print("Agent %d took too long to make a move! This is warning %d" % (agentIndex, self.totalAgentTimeWarnings[agentIndex]), file=sys.stderr)
                        if self.totalAgentTimeWarnings[agentIndex] > self.rules.getMaxTimeWarnings(agentIndex):
                            print("Agent %d exceeded the maximum number of warnings: %d" % (agentIndex, self.totalAgentTimeWarnings[agentIndex]), file=sys.stderr)
                            self.agentTimeout = True
                            self._agentCrash(agentIndex, quiet=True)
                            self.unmute()
                            return

                    self.totalAgentTimes[agentIndex] += move_time
                    #print("Agent: %d, time: %f, total: %f" % (agentIndex, move_time, self.totalAgentTimes[agentIndex]))
                    if self.totalAgentTimes[agentIndex] > self.rules.getMaxTotalTime(agentIndex):
                        print("Agent %d ran out of time! (time: %1.2f)" % (agentIndex, self.totalAgentTimes[agentIndex]), file=sys.stderr)
                        self.agentTimeout = True
                        self._agentCrash(agentIndex, quiet=True)
                        self.unmute()
                        return
                    self.unmute()
                except Exception as data:
                    self._agentCrash(agentIndex)
                    self.unmute()
                    return
            else:
                action = agent.getAction(observation)
            self.unmute()

            # Execute the action
            self.moveHistory.append( (agentIndex, action) )
            if self.catchExceptions:
                try:
                    self.state = self.state.produce_successor( agentIndex, action )
                except Exception as data:
                    self.mute(agentIndex)
                    self._agentCrash(agentIndex)
                    self.unmute()
                    return
            else:
                self.state = self.state.produce_successor( agentIndex, action )

            # Change the display
            self.display.update( self.state.data )
            ###idx = agentIndex - agentIndex % 2 + 1
            ###self.display.update( self.state.makeObservation(idx).data )

            # Allow for game specific conditions (winning, losing, etc.)
            self.rules.process(self.state, self)
            # Track progress
            if agentIndex == numAgents + 1: self.numMoves += 1
            # Next agent
            agentIndex = ( agentIndex + 1 ) % numAgents

            if _BOINC_ENABLED:
                boinc.set_fraction_done(self.getProgress())

        # inform a learning agent of the game result
        for agentIndex, agent in enumerate(self.agents):
            if "final" in dir( agent ) :
                try:
                    self.mute(agentIndex)
                    agent.final( self.state )
                    self.unmute()
                except Exception as data:
                    if not self.catchExceptions: raise data
                    self._agentCrash(agentIndex)
                    self.unmute()
                    return
        self.display.finish()
