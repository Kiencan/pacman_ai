from state import movement
from state import Agent
from state import Actions
import utility_functions
import time
import pacman_types
from pacman import *
import terminal


class GoWestAgent(Agent):
    def getAction(self, state):
        if movement.left in state.get_legal_pac_moves():
            return movement.left        
        else:
            return movement.STOP

class SearchAgent(Agent):
    def __init__(self, fn='depthFirstSearch', prob='PositionSearchProblem', heuristic='nullHeuristic'):
        if fn not in dir(pacman_types):
            raise AttributeError(fn + ' is not a search function in pacman_types.py.')
        func = getattr(pacman_types, fn)
        if 'heuristic' not in func.__code__.co_varnames:
            # terminal.print_text('Tác tử tìm kiếm sử dụng ' + fn)
            print('Tác tử tìm kiếm sử dụng ' + fn)
            self.searchFunction = func
        else:
            if heuristic in globals().keys():
                heur = globals()[heuristic]
            elif heuristic in dir(pacman_types):
                heur = getattr(pacman_types, heuristic)
            else:
                raise AttributeError(heuristic + ' is not a function in search_types.py or pacman_types.py.')
            # terminal.print_text('Tác tử tìm kiếm sử dụng %s và hàm Heuristic %s' % (fn, heuristic))
            print('Tác tử tìm kiếm sử dụng %s và hàm Heuristic %s' % (fn, heuristic))
            self.searchFunction = lambda x: func(x, heuristic=heur)

        if prob not in globals().keys() or not prob.endswith('Problem'):
            raise AttributeError(prob + ' is not a search problem type in SearchAgents.py.')
        self.searchType = globals()[prob]
        print('Tác tử tìm kiếm giải quyết vấn đề ' + prob)

    def registerInitialState(self, state):
        if self.searchFunction == None: raise Exception("No search function provided for SearchAgent")
        starttime = time.time()
        problem = self.searchType(state) # Makes a new search problem
        self.actions  = self.searchFunction(problem) # Find a path
        totalCost = problem.getCostOfActions(self.actions)
        # terminal.print_text('Con đường tìm được với tổng chi phí là %d trong %.3f giây' % (totalCost, time.time() - starttime))
        print('Con đường tìm được với tổng chi phí là %d trong %.3f giây' % (totalCost, time.time() - starttime))
        if '_expanded' in dir(problem): 
            # terminal.print_text('Số nodes tìm kiếm: %d' % problem._expanded)
            print('Số nodes tìm kiếm: %d' % problem._expanded)

    def getAction(self, state):
        if 'actionIndex' not in dir(self): self.actionIndex = 0
        i = self.actionIndex
        self.actionIndex += 1
        if i < len(self.actions):
            return self.actions[i]
        else:
            return movement.STOP


class PositionSearchProblem(pacman_types.SearchProblem):
    def __init__(self, gameState, costFn = lambda x: 1, goal=(1,1), start=None, warn=True, visualize=True):
        self.walls = gameState.get_walls()
        self.startState = gameState.get_pacman_coord()
        if start != None: self.startState = start
        self.goal = goal
        self.costFn = costFn
        self.visualize = visualize
        if warn and (gameState.remaining_coin() != 1 or not gameState.has_coin(*goal)):
            # terminal.print_text('Warning: this does not look like a regular search maze')
            print('Warning: this does not look like a regular search maze')

        # For display purposes
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):
        isGoal = state == self.goal

        # For display purposes only
        if isGoal and self.visualize:
            self._visitedlist.append(state)
            import __main__
            if '_display' in dir(__main__):
                if 'drawExpandedCells' in dir(__main__._display): #@UndefinedVariable
                    __main__._display.drawExpandedCells(self._visitedlist) #@UndefinedVariable

        return isGoal

    def getSuccessors(self, state):
        successors = []
        for action in [movement.up, movement.down, movement.right, movement.left]:
            x,y = state
            dx, dy = Actions.direction_from_vector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = self.costFn(nextState)
                successors.append(( nextState, action, cost))

        # Bookkeeping for display purposes
        self._expanded += 1 # DO NOT CHANGE
        if state not in self._visited:
            self._visited[state] = True
            self._visitedlist.append(state)

        return successors

    def getCostOfActions(self, actions):
        if actions == None: return 999999
        x,y= self.getStartState()
        cost = 0
        for action in actions:
            # Check figure out the next state and see whether its' legal
            dx, dy = Actions.direction_from_vector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
            cost += self.costFn((x,y))
        return cost


class StayEastSearchAgent(SearchAgent):
    def __init__(self):
        self.searchFunction = pacman_types.uniformCostSearch
        costFn = lambda pos: .5 ** pos[0]
        self.searchType = lambda state: PositionSearchProblem(state, costFn, (1, 1), None, False)


class StayWestSearchAgent(SearchAgent):
    def __init__(self):
        self.searchFunction = pacman_types.uniformCostSearch
        costFn = lambda pos: 2 ** pos[0]
        self.searchType = lambda state: PositionSearchProblem(state, costFn)

def manhattanHeuristic(position, problem, info={}):
    xy1 = position
    xy2 = problem.goal
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])

def euclideanHeuristic(position, problem, info={}):
    xy1 = position
    xy2 = problem.goal
    return ((xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2) ** 0.5


class CornersProblem(pacman_types.SearchProblem):
    def __init__(self, startingGameState):
        self.walls = startingGameState.get_walls()
        self.startingPosition = startingGameState.get_pacman_coord()
        top, right = self.walls.height-2, self.walls.width-2
        self.corners = ((1,1), (1,top), (right, 1), (right, top))
        for corner in self.corners:
            if not startingGameState.has_coin(*corner):
                print('Warning: no food in corner ' + str(corner))
        self._expanded = 0 # DO NOT CHANGE; Number of search nodes expanded

    def getStartState(self):
        visitedCorners = [ False for c in self.corners]     # At start, all corners are unvisited
        startState = (self.startingPosition, tuple(visitedCorners))
        return startState

    def isGoalState(self, state):
        if False in state[1]:
            return False
        return True


    def getSuccessors(self, state):
        successors = []
        for action in [movement.up, movement.down, movement.right, movement.left]:
            parentX, parentY = state[0]
            dx, dy = Actions.direction_from_vector(action)
            successorX, successorY = int(parentX + dx), int(parentY + dy)
            hitsWall = self.walls[successorX][successorY]

            if not hitsWall:
                successorCornerState = list(state[1])
                if (successorX, successorY) in self.corners:
                    cornerIndex = self.corners.index( (successorX, successorY) )
                    successorCornerState[cornerIndex] = True

                successorState = ( (successorX, successorY), tuple(successorCornerState) )
                successors.append((successorState, action, 1))

        self._expanded += 1 # DO NOT CHANGE
        return successors

    def getCostOfActions(self, actions):
        if actions == None: return 999999
        x,y= self.startingPosition
        for action in actions:
            dx, dy = Actions.direction_from_vector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
        return len(actions)


def cornersHeuristic(state, problem: CornersProblem):
    corners = problem.corners                   # These are the corner coordinates
    walls = problem.walls                       # These are the walls of the maze, as a Grid (game.py)

    if problem.isGoalState(state):
        return 0                                # Return 0 in case of a goal state
    
    visited = state[1]                          # Store the visited corners tuple here
    maxCornerDistance = -1
    for i in range(0, len(corners)):            # Iterating through the corners tuple
        if visited[i]:                          # Skip in case this corner is visited
            continue
        cornerDistance = manhattanDistance(state[0], corners[i])    # Not visited, so find the distance form the current state
        if cornerDistance > maxCornerDistance:
            maxCornerDistance = cornerDistance
    
    return maxCornerDistance

def manhattanDistance(posA, posB):
    return abs(posA[0] - posB[0]) + abs(posA[1] - posB[1])

def euclideanDistance( posA, posB ):
    return ((posA[0] - posB[0])**2 + (posA[1] - posB[1])**2 )**0.5

class AStarCornersAgent(SearchAgent):
    def __init__(self):
        self.searchFunction = lambda prob: pacman_types.aStarSearch(prob, cornersHeuristic)
        self.searchType = CornersProblem


class FoodSearchProblem:
    def __init__(self, startingGameState):
        self.start = (startingGameState.get_pacman_coord(), startingGameState.get_coin())
        self.walls = startingGameState.get_walls()
        self.startingGameState = startingGameState
        self._expanded = 0 # DO NOT CHANGE
        self.heuristicInfo = {} # A dictionary for the heuristic to store information

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return state[1].count() == 0

    def getSuccessors(self, state):
        successors = []
        self._expanded += 1 # DO NOT CHANGE
        for direction in [movement.up, movement.down, movement.right, movement.left]:
            x,y = state[0]
            dx, dy = Actions.direction_from_vector(direction)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextFood = state[1].copy()
                nextFood[nextx][nexty] = False
                successors.append((((nextx, nexty), nextFood), direction, 1))
        return successors

    def getCostOfActions(self, actions):
        x,y= self.getStartState()[0]
        cost = 0
        for action in actions:
            # figure out the next state and see whether it's legal
            dx, dy = Actions.movement(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]:
                return 999999
            cost += 1
        return cost

class AStarFoodSearchAgent(SearchAgent):
    def __init__(self):
        self.searchFunction = lambda prob: pacman_types.aStarSearch(prob, foodHeuristic)
        self.searchType = FoodSearchProblem


def foodHeuristic(state, problem: FoodSearchProblem):
    if problem.isGoalState(state):
        return 0                                # Return 0 in case of a goal state
    
    position, foodGrid = state                  # Get the parent position and food Grid
    food = foodGrid.as_list()
    maxDistance = 0

    first = food[0]
    second = food[0]
    for i in range(len(food)):
        for j in range(i + 1, len(food)):
            dist = manhattanDistance(food[i], food[j])
            if dist > maxDistance:
                maxDistance = dist
                first = food[i]
                second = food[j]
    
    return maxDistance + min((manhattanDistance(position, first), manhattanDistance(position, second)))

class ClosestDotSearchAgent(SearchAgent):
    def registerInitialState(self, state):
        self.actions = []
        currentState = state
        while(currentState.get_coin().count() > 0):
            nextPathSegment = self.findPathToClosestDot(currentState) # The missing piece
            self.actions += nextPathSegment
            for action in nextPathSegment:
                legal = currentState.get_legal_moves()
                if action not in legal:
                    t = (str(action), str(currentState))
                    raise Exception('findPathToClosestDot returned an illegal move: %s!\n%s' % t)
                currentState = currentState.produce_successor(0, action)
        self.actionIndex = 0
        print('Path found with cost %d.' % len(self.actions))

    def findPathToClosestDot(self, gameState):
        # Here are some useful elements of the startState
        startPosition = gameState.get_pacman_coord()
        food = gameState.get_coin()
        walls = gameState.get_walls()
        problem = AnyFoodSearchProblem(gameState)

        # Solving the problem using BFS, is the most suitable choice
        return pacman_types.breadthFirstSearch(problem)


class AnyFoodSearchProblem(PositionSearchProblem):
    def __init__(self, gameState):
        # Store the food for later reference
        self.food = gameState.get_coin()

        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = gameState.get_walls()
        self.startState = gameState.get_pacman_coord()
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def isGoalState(self, state):
        x,y = state         # Any state with a food dot, is also a goal state
        return self.food[x][y]


def mazeDistance(point1, point2, gameState):
    x1, y1 = point1
    x2, y2 = point2
    walls = gameState.get_walls()
    assert not walls[x1][y1], 'point1 is a wall: ' + str(point1)
    assert not walls[x2][y2], 'point2 is a wall: ' + str(point2)
    prob = PositionSearchProblem(gameState, start=point1, goal=point2, warn=False, visualize=False)
    return len(pacman_types.bfs(prob))
