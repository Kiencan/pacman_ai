from utility_functions import *
from state import movement
import random, utility_functions
import utility_functions
from state import Agent
# from search_types import manhattanHeuristic, euclideanHeuristic

class reflex_agent(Agent):

    def getAction(self, game_state):

        def remove_stop(List):
            return [x for x in List if x != 'Stop']
        
        legal_moves = remove_stop(game_state.get_legal_moves())

        scores = [self.reflex_evaluator(game_state, action) for action in legal_moves] 
        max_score = max(scores) 
        max_score_indexs = [index for index in range(len(scores)) if
                       scores[index] == max_score] 
        random_index = random.choice(max_score_indexs) 
        return legal_moves[random_index]

    def reflex_evaluator(self, current_game_state, action):

        # returns a score,the higher the score from reflex_evaluator the better
        # information taken into consideration from current state: remaining coin(new_coin), Pacman position after moving (new_coord), ScaredTimes of the ghosts

        next_game_state = current_game_state.produce_pac_successor(action)
        loc = next_game_state.get_pacman_coord()  # taking the pacman position after moving
        coin = next_game_state.get_coin()  # taking the remaining coin
        ghosts = next_game_state.get_ghost_states() # taking the ghost states
        walls = next_game_state.get_walls()

        dmap = walls.copy()
        stk = utility_functions.Queue()
        stk.push(loc)
        dmap[loc[0]][loc[1]] = 0
        dis = 0
        while not stk.isEmpty():  # Using BFS inorder to find the closest coin available
            x , y = stk.pop()
            dis = dmap[x][y] + 1
            if coin[x][y]:
                break;
            for v in [(0, 1) , (1, 0) , (0 , -1) , (-1 , 0)]:
                xn = x + v[0]
                yn = y + v[1]
                if dmap[xn][yn] == False:
                    dmap[xn][yn] = dis
                    stk.push((xn, yn))
        if(coin.count() == 0):
            dis = 1
        score = 1 - dis
        for ghost in ghosts:
            if ghost.scared_timer == 0:  # active ghost poses danger to the pacman
                score -= 100 ** (1.6 - coords_distance(ghost.get_coord(), loc))
            else:  # bonus points for having a scared ghost
                score += 25
        score -= 30 * coin.count() # bonus points for eating a coin
        return score  # next_game_state.get_score()

# class reflex_agent(Agent):

#     def getAction(self, game_state):
        
#         legal_moves = game_state.get_legal_moves()

#         scores = [self.reflex_evaluator(game_state, action) for action in legal_moves] 
#         max_score = max(scores) 
#         max_score_indexs = [index for index in range(len(scores)) if scores[index] == max_score] 
#         random_index = random.choice(max_score_indexs) 
#         return legal_moves[random_index]

#     def reflex_evaluator(self, current_game_state, action):

#         successor_game_state = current_game_state.produce_pac_successor(action)
#         new_pos = successor_game_state.get_pacman_coord()
#         current_coin = successor_game_state.get_coin()
#         ghosts = successor_game_state.get_ghost_coords()

#         for p in ghosts:
#             if p == new_pos or utility_functions.coords_distance(p, new_pos) == 1:
#                 return(float('-inf'))
#             elif current_coin[new_pos[0]][new_pos[1]]:
#                 return float('inf')
        
#         min_distance = float('inf')
#         coin = current_coin.as_list()
#         for c in coin:
#             dist = utility_functions.coords_distance(c, new_pos)
#             if dist < min_distance:
#                 min_distance = dist
        
#         return -min_distance

def multiAgent_evaluator(current_game_state):

    if current_game_state.pac_won():
        return 1000000
    elif current_game_state.pac_lost():
        return -1000000

    loc = current_game_state.get_pacman_coord()     
    coin = current_game_state.get_coin() # getting the coin locations
    walls = current_game_state.get_walls() # getting the wall locations
    dmap = walls.copy()
    stk = utility_functions.Queue()
    stk.push(loc)
    dmap[loc[0]][loc[1]] = 0
    dis = 0
    while not stk.isEmpty():  # Using BFS inorder to find the closest coin available
        x , y = stk.pop()
        dis = dmap[x][y] + 1
        if coin[x][y]:
            break;
        for v in [(0, 1) , (1, 0) , (0 , -1) , (-1 , 0)]:
            xn = x + v[0]
            yn = y + v[1]
            if dmap[xn][yn] == False:
                dmap[xn][yn] = dis
                stk.push((xn, yn))
    if(coin.count() == 0):
        dis = 1
    score = 1 - dis
    ghosts = current_game_state.get_ghost_states() # getting ghost states
    for ghost in ghosts:
        if ghost.scared_timer == 0:  # active ghost poses danger to the pacman
            score -= 100 ** (1.6 - coords_distance(ghost.get_coord(), loc))
        else:  # bonus points for having a scared ghost
            score += 25
    score -= 30 * coin.count()  # bonus points for eating a coin
    return score

class mutli_agent_search(Agent):
    # Some variables and methods that are publically available to all Minimax, alpha_beta_agent, and expecti_max_agent
    def __init__(self, evalFn='multiAgent_evaluator', depth='2'):
        self.index = 0  # Pacman is always agent index 0
        self.reflex_evaluator = utility_functions.lookup(evalFn, globals())
        self.depth = int(depth)  # the depth till which the game_state will be evaluated. The more the depth, the more accurate the result, however, time taken would be greater as more branches would be traversed

class minimax_agent(mutli_agent_search):
    def getAction(self, game_state):
        num_agent = game_state.get_num_agents() 
        action_score = []

        def remove_stop(List): 
            return [x for x in List if x != 'Stop']

        def miniMax(s, iteration_count):  # default depth is '2'
            if iteration_count >= self.depth * num_agent or s.pac_won() or s.pac_lost(): 
                return self.reflex_evaluator(s)
            if iteration_count % num_agent != 0:
                result = 1e10
                for a in remove_stop(s.get_legal_moves(iteration_count % num_agent)):
                    successor_data = s.produce_successor(iteration_count % num_agent, a) 
                    result = min(result, miniMax(successor_data, iteration_count + 1))
                return result
            else: 
                result = -1e10 
                for a in remove_stop(s.get_legal_moves(iteration_count % num_agent)):
                    successor_data = s.produce_successor(iteration_count % num_agent, a)
                    result = max(result, miniMax(successor_data,
                                                  iteration_count + 1)) 
                    if iteration_count == 0:
                        action_score.append(result)
                return result

        result = miniMax(game_state, 0)
        return remove_stop(game_state.get_legal_moves(0))[
            action_score.index(max(action_score))]

class alpha_beta_agent(mutli_agent_search):
    # ALPHA BETA AGENT
    def getAction(self, game_state):
        # Main Code
        num_agent = game_state.get_num_agents()
        action_score = []

        def remove_stop(List):
            return [x for x in List if x != 'Stop']

        # introduced two factor, alpha and beta here, in order to prune and not traverse all gamestates
        def alpha_beta(s, iteration_count, alpha, beta):
            if iteration_count >= self.depth * num_agent or s.pac_won() or s.pac_lost():
                return self.reflex_evaluator(s)
            if iteration_count % num_agent != 0:  # Ghost min
                result = 1e10
                for a in remove_stop(s.get_legal_moves(iteration_count % num_agent)):
                    successor_data = s.produce_successor(iteration_count % num_agent, a)
                    result = min(result, alpha_beta(successor_data, iteration_count + 1, alpha, beta))
                    beta = min(beta, result)  # beta holds the minimum of the path travered till the root
                    if beta < alpha:  # Pruning. If beta is lesser than alpha, then we need not to traverse the other state
                        break
                return result
            else:  # Pacman Max
                result = -1e10
                for a in remove_stop(s.get_legal_moves(iteration_count % num_agent)):
                    successor_data = s.produce_successor(iteration_count % num_agent, a)
                    result = max(result, alpha_beta(successor_data, iteration_count + 1, alpha, beta))
                    alpha = max(alpha, result)  # alpha holds the maxmimum of the path travered till the root
                    if iteration_count == 0:
                        action_score.append(result)
                    if beta < alpha:  # Prunning
                        break
                return result

        result = alpha_beta(game_state, 0, -1e20, 1e20)  # alpha and beta are set to -ve and +ve infinity as shown
        return remove_stop(game_state.get_legal_moves(0))[action_score.index(max(action_score))]

class expecti_max_agent(mutli_agent_search):
    # EXPECTIMAX AGENT
    def getAction(self, game_state):
        # Main Code
        num_agent = game_state.get_num_agents()
        action_score = []

        def remove_stop(List):
            return [x for x in List if x != 'Stop']

        def expect_minimax(s, iteration_count):
            if iteration_count >= self.depth * num_agent or s.pac_won() or s.pac_lost():
                return self.reflex_evaluator(s)
            if iteration_count % num_agent != 0:  # Ghost min
                successor_score = []
                for a in remove_stop(s.get_legal_moves(iteration_count % num_agent)):
                    successor_data = s.produce_successor(iteration_count % num_agent, a)
                    result = expect_minimax(successor_data, iteration_count + 1)
                    successor_score.append(result)
                avg_score = sum([float(x) / len(successor_score) for x in
                                    successor_score])  # maintaing the average of the scores instead of the max or min
                return avg_score
            else:  # Pacman Max
                result = -1e10
                for a in remove_stop(s.get_legal_moves(iteration_count % num_agent)):
                    successor_data = s.produce_successor(iteration_count % num_agent, a)
                    result = max(result, expect_minimax(successor_data, iteration_count + 1))
                    if iteration_count == 0:
                        action_score.append(result)
                return result

        result = expect_minimax(game_state, 0);
        return remove_stop(game_state.get_legal_moves(0))[action_score.index(max(action_score))]


class SearchProblem:

    def getStartState(self):
        utility_functions.raiseNotDefined()

    def isGoalState(self, state):
        utility_functions.raiseNotDefined()

    def getSuccessors(self, state):
        utility_functions.raiseNotDefined()

    def getCostOfActions(self, actions):
        utility_functions.raiseNotDefined()


def tinyMazeSearch(problem):
    from state import movement
    s = movement.up
    w = movement.left
    return  [s, s, w, s, w, w, s, w]

# def depthFirstSearch(problem: SearchProblem):
#     currPath = []
#     currState =  problem.getStartState()

#     if problem.isGoalState(currState):
#         return currPath

#     frontier = Stack()
#     frontier.push((currState, currPath))
#     explored = set()
#     while not frontier.isEmpty():
#         currState, currPath = frontier.pop()
#         if problem.isGoalState(currState):
#             return currPath
        
#         explored.add(currState)
#         for s in problem.getSuccessors(currState):
#             if s[0] not in explored:
#                 frontier.push((s[0], currPath +[s[1]]))

#     return []

def depthFirstSearch(problem: SearchProblem):
    action = []
    visited = {}
    cost = 0
    frontier = Stack()
    start_node =  problem.getStartState()
    if problem.isGoalState(start_node): 
        return action
    
    frontier.push((start_node, action, cost))

    while not frontier.isEmpty():
        current = frontier.pop()
        if problem.isGoalState(current[0]):
            return current[1]
        
        if current[0] not in visited:
            visited[current[0]] = True
            for next, act, co in problem.getSuccessors(current[0]):
                if next and next not in visited:
                    frontier.push((next, current[1] + [act], current[2] + co))

    utility_functions.raiseNotDefined()

# def breadthFirstSearch(problem: SearchProblem):
#     currPath = []
#     currState =  problem.getStartState() 

#     if problem.isGoalState(currState): 
#         return currPath

#     frontier = Queue()
#     frontier.push((currState, currPath))  
#     explored = set()
#     while not frontier.isEmpty():
#         currState, currPath = frontier.pop() 
#         if problem.isGoalState(currState):
#             return currPath
#         explored.add(currState)
#         frontierStates = [t[0] for t in frontier.list]
#         for s in problem.getSuccessors(currState):
#             if s[0] not in explored and s[0] not in frontierStates:
#                 frontier.push((s[0], currPath + [s[1]])) 
#     return []
def breadthFirstSearch(problem: SearchProblem):
    action = []
    visited = {}
    cost = 0
    frontier = Queue()
    start_node =  problem.getStartState()
    if problem.isGoalState(start_node): 
        return action
    
    frontier.push((start_node, action, cost))
    while not frontier.isEmpty():
        current = frontier.pop()
        if problem.isGoalState(current[0]):
            return current[1]
        
        if current[0] not in visited:
            visited[current[0]] = True
            for next, act, co in problem.getSuccessors(current[0]):
                if next and next not in visited:
                    frontier.push((next, current[1] + [act], current[2] + co))

    utility_functions.raiseNotDefined()

# def uniformCostSearch(problem: SearchProblem):
#     currPath = []
#     currState = problem.getStartState()
#     frontier = PriorityQueue()
#     frontier.push((currState, currPath), 0)
#     explored = set()

#     while not frontier.isEmpty():
#         currState, currPath = frontier.pop()
#         if problem.isGoalState(currState):
#             return currPath
#         explored.add(currState)
#         frontierStates = [i[2][0] for i in frontier.heap]
#         for s in problem.getSuccessors(currState):
#             successorPath = currPath + [s[1]]
#             if s[0] not in explored and s[0] not in frontierStates:
#                 frontier.push( (s[0], successorPath), problem.getCostOfActions(successorPath) )
#             else:
#                 for i in range(0, len(frontierStates)):
#                     if s[0] == frontierStates[i]:
#                         updatedCost = problem.getCostOfActions(successorPath)
#                         storedCost = frontier.heap[i][0]
#                         if storedCost > updatedCost:
#                             frontier.heap[i] = (storedCost, frontier.heap[i][1] , (s[0], successorPath) )
#                             frontier.update( (s[0], successorPath), updatedCost )

#     return []

def uniformCostSearch(problem: SearchProblem):
    action = []
    visited = {}
    cost = 0
    frontier = PriorityQueue()
    start_node =  problem.getStartState()
    if problem.isGoalState(start_node):
        return action
    
    frontier.push((start_node, action, cost), cost)
    while not frontier.isEmpty():
        current = frontier.pop()
        if problem.isGoalState(current[0]):
            return current[1]
        
        if current[0] not in visited:
            visited[current[0]] = True
            for next, act, co in problem.getSuccessors(current[0]):
                if next and next not in visited:
                    frontier.push((next, current[1] + [act], current[2] + co), current[2] + co)

    utility_functions.raiseNotDefined()

def nullHeuristic(state, problem=None):
    return 0

def evalFunction(problem: SearchProblem, state, actions, heuristicFunction):
    return problem.getCostOfActions(actions) + heuristicFunction(state, problem)

# def aStarSearch(problem: SearchProblem, heuristic = nullHeuristic, eval = evalFunction):
#     currPath = [] 
#     currState = problem.getStartState()
#     frontier = PriorityQueue()
#     frontier.push((currState, currPath), eval(problem, currState, currPath, heuristic))
#     explored = set()

#     while not frontier.isEmpty():
#         currState, currPath = frontier.pop()
#         if problem.isGoalState(currState):
#             return currPath
#         explored.add(currState)
#         frontierStates = [ i[2][0] for i in frontier.heap]
#         for s in problem.getSuccessors(currState):
#             successorPath = currPath + [s[1]]
#             if s[0] not in explored and s[0] not in frontierStates:
#                 frontier.push( (s[0], successorPath), eval(problem, s[0], successorPath, heuristic))
#             else:
#                 for i in range(0, len(frontierStates)):
#                     if s[0] == frontierStates[i]:
#                         updatedCost = eval(problem, s[0], successorPath, heuristic)
#                         storedCost = frontier.heap[i][0]
#                         if storedCost > updatedCost:
#                             frontier.heap[i] = (storedCost, frontier.heap[i][1] , (s[0], successorPath))
#                             frontier.update( (s[0], successorPath), updatedCost)

#     return []

def aStarSearch(problem: SearchProblem, heuristic=nullHeuristic):
    action = []
    visited = {}
    cost = 0
    frontier = PriorityQueue()
    start_node =  problem.getStartState()
    if problem.isGoalState(start_node): 
        return action
    
    frontier.push((start_node, action, cost), cost)
    while not frontier.isEmpty():
        current = frontier.pop()
        if problem.isGoalState(current[0]):
            return current[1]
        
        if current[0] not in visited:
            visited[current[0]] = True
            for next, act, co in problem.getSuccessors(current[0]):
                if next and next not in visited:
                    frontier.push((next, current[1] + [act], current[2] + co), current[2] + heuristic(next, problem) + co)

    utility_functions.raiseNotDefined()


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch

class LeftTurnAgent(Agent):
    "An agent that turns left at every opportunity"

    def getAction(self, state):
        legal = state.getLegalPacmanActions()
        current = state.getPacmanState().configuration.direction
        if current == movement.STOP: current = movement.up
        left = movement.left_dir[current]
        if left in legal: return left
        if current in legal: return current
        if movement.right_dir[current] in legal: return movement.right_dir[current]
        if movement.left_dir[left] in legal: return movement.left_dir[left]
        return movement.STOP

class GreedyAgent(Agent):
    def __init__(self, evalFn="scoreEvaluation"):
        self.evaluationFunction = utility_functions.lookup(evalFn, globals())
        assert self.evaluationFunction != None

    def getAction(self, state):
        # Generate candidate actions
        legal = state.get_legal_pac_moves()
        if movement.STOP in legal: legal.remove(movement.STOP)

        successors = [(state.produce_successor(0, action), action) for action in legal]
        scored = [(self.evaluationFunction(state), action) for state, action in successors]
        bestScore = max(scored)[0]
        bestActions = [pair[1] for pair in scored if pair[0] == bestScore]
        return random.choice(bestActions)

def scoreEvaluation(state):
    return state.get_score()