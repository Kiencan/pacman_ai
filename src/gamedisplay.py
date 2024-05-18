from gamegraphics import *
import math, time
from state import movement

#Settings for the display
grid_size = 15
info_height = 35
background_c= format_color(0,0,0)
wall_c = format_color(0.0/255.0, 51.0/255.0, 255.0/255.0)
ip_c = format_color(.4, .4, 0)
score_c = format_color(.9, .9, .9)
pac_outline = 2
pac_capture_outline = 4


#Settings for Ghost
ghost_c = []
ghost_c.append(format_color(.9,0,0)) # Red
ghost_c.append(format_color(0,.3,.9)) # Blue
ghost_c.append(format_color(.98,.41,.07)) # Orange
ghost_c.append(format_color(.1,.75,.7)) # Green
ghost_c.append(format_color(1.0,0.6,0.0)) # Yellow
ghost_c.append(format_color(.4,0.13,0.91)) # Purple

team_c = ghost_c[:2]

#defines the dimensions of the ghost
# ghost_dimensions = [
#     (0, 1),
#     (1, 0),
#     (0, - 1),
#     (-1, 0),
#   ]
ghost_dimensions = [
    (0,     0.3),
    (0.25,  0.75),
    (0.5,   0.3),
    (0.75,  0.75),
    (0.75,  -0.5),
    (0.5,   -0.75),
    (-0.5,  -0.75),
    (-0.75, -0.5),
    (-0.75, 0.75),
    (-0.5,  0.3),
    (-0.25, 0.75)
]

ghost_s = 0.65
scare_c = format_color(1,1,1)
ghost_vect_c = [color_to_vector(c) for c in ghost_c]

#Some attributes of Pacman
pac_c = format_color(255.0/255.0, 255.0/255.0, 61.0/255)
pac_s = 0.5
#pacman_speed = 0.25

#coin location
coin_c = format_color(1,1,1)
coin_s = 0.1

# Laser
laser_c = format_color(1, 0, 0)
laser_s = 0.02

#bcoin location
big_coin_c = format_color(1, 1, 1)
big_coin_s = 0.25

#wall location
wall_r = 0.15

class info_p:
    def __init__(self, maze, grid_size):
        #Starting pane attributes
        self.grid_size = grid_size
        self.width = (maze.width) * grid_size
        self.base = (maze.height + 1) * grid_size
        self.height = info_height
        self.font_size = 24
        self.text_c = pac_c
        self.draw_pane()

    def to_screen(self, coord, y = None): #Maps the positions from maze onto the screen
        if y == None:
            x,y = coord
        else:
            x = coord

        x = self.grid_size + x # Margin
        y = self.base + y
        return x,y

    def draw_pane(self):
        self.score_text = text( self.to_screen(0, 0), self.text_c, "Diểm:    0", "Times", self.font_size, "bold")

    def initialize_ghost_distances(self, distances): #initializing ghost onto the screen
        self.ghost_distance_text = []

        size = 20
        if self.width < 240:
            size = 12
        if self.width < 160:
            size = 10

        for i, d in enumerate(distances):
            t = text( self.to_screen(self.width/2 + self.width/8 * i, 0), ghost_c[i+1], d, "Times", size, "bold")
            self.ghost_distance_text.append(t)

    def update_score(self, score):
        change_text(self.score_text, "Điểm: % 4d" % score)

    def setTeam(self, isBlue):
        text = "RED TEAM"
        if isBlue:
            text = "BLUE TEAM"
        self.teamText = text(self.toScreen(
            300, 0), self.text_c, text, "Times", self.font_size, "bold")

    def update_ghost_distances(self, distances):
        if len(distances) == 0:
            return
        if 'ghost_distance_text' not in dir(self): 
            self.initialize_ghost_distances(distances)
        else:
            for i, d in enumerate(distances):
                change_text(self.ghost_distance_text[i], d)
    
    def make_ghost(self):
        pass

    def make_pac(self):
        pass

    def make_warn(self):
        pass

    def clear_icon(self):
        pass

    def update_message(self, message):
        pass

    def clear_message(self):
        pass

class pac_graphic: #general graphics for pacman
    def __init__(self, zoom = 1.0, frame_t=0.0, capture = False):
        self.have_window = 0
        self.currentGhostImages = {}
        self.pacmanImage = None
        self.zoom = zoom
        self.grid_size = grid_size * zoom
        self.capture = capture
        self.frame_t = frame_t
        
    def checkNullDisplay(self):
        return False

    def initialize(self, state, isBlue = False):
        self.isBlue = isBlue
        self.start_graphic(state)
        self.distributionImages = None  # Initialized lazily
        self.make_static_obj(state)
        self.make_agent_obj(state)

        # Information
        self.previousState = state

    def start_graphic(self, state): #initializing the graphics onto the screen
        self.maze = state.maze
        maze = self.maze
        self.width = maze.width
        self.height = maze.height
        self.make_window(self.width, self.height)
        self.info_p = info_p(maze, self.grid_size)
        self.c_state = maze

    def draw_distributions(self, state):
        walls = state.maze.walls
        dist = []
        for x in range(walls.width):
            distx = []
            dist.append(distx)
            for y in range(walls.height):
                (screen_x, screen_y) = self.to_screen((x, y))
                block = square((screen_x, screen_y),
                               0.5 * self.grid_size,
                               color=background_c,
                               filled=1, behind=2)
                distx.append(block)
        self.distributionImages = dist

    #drawing coin and bcoin onto the screen
    def make_static_obj(self, state):
        maze = self.maze
        self.make_wall(maze.walls)
        self.coin = self.make_coin(maze.coin)
        self.big_coin = self.make_big_coin(maze.big_coin)
        refresh()

    #drawing the pacman, ghost onto the screen
    def make_agent_obj(self, state):
        self.agent_img = [] # (agentState, image)
        for index, agent in enumerate(state.agent_states):
            if agent.is_pac:
                image = self.make_pac(agent, index)
                self.agent_img.append((agent, image))
            else:
                image = self.make_ghost(agent, index)
                self.agent_img.append((agent, image))
        refresh()

    def swap_images(self, agent_index, new_state):
        """
          Changes an image from a ghost to a pacman or vis versa (for capture)
        """
        prevState, prevImage = self.agent_img[agent_index]
        for item in prevImage:
            remove_from_screen(item)
        if new_state.is_pac:
            image = self.make_pac(new_state, agent_index)
            self.agent_img[agent_index] = (new_state, image)
        else:
            image = self.make_ghost(new_state, agent_index)
            self.agent_img[agent_index] = (new_state, image)
        refresh()

    #updates c_state to the new_state recieved
    def update(self, new_state):
        #updating the agent moved
        agent_index = new_state.agent_moved
        agent_state = new_state.agent_states[agent_index]

        if self.agent_img[agent_index][0].is_pac != agent_state.is_pac:
            self.swap_images(agent_index, agent_state)

        prevState, prevImage = self.agent_img[agent_index]

        if agent_state.is_pac:
            self.animate_pacman_movement(agent_state, prevState, prevImage) #moving pacman
        else:
            self.move_ghost(agent_state, agent_index, prevState, prevImage) #animating or moving the ghost

        self.agent_img[agent_index] = (agent_state, prevImage)

        if new_state.coin_eaten != None:
            self.rem_coin(new_state.coin_eaten, self.coin) #if the coin is eaten, remove it from its position in new state
        if new_state.big_food_Eaten != None:
            self.remove_big_food(new_state.big_food_Eaten, self.big_coin) #same as coin
        self.info_p.update_score(new_state.score)
        if 'ghost_distances' in dir(new_state):
            self.info_p.update_ghost_distances(new_state.ghost_distances) #updating the ghost distances here

    def make_window(self, width, height): #initializing the screen
        grid_width = (width-1) * self.grid_size
        grid_height = (height-1) * self.grid_size
        screen_width = 2*self.grid_size + grid_width
        screen_height = 2*self.grid_size + grid_height + info_height

        #starting the screen
        begin_graphics(screen_width,
                       screen_height,
                       background_c,
                       "PACMAN MULTI-AGENT SIMULATION")

    #drawing the pacman
    def make_pac(self, pacman, index):
        position = self.get_coord(pacman)
        screen_point = self.to_screen(position)
        end_coord = self.get_end_coord(self.get_dir(pacman))

        width = pac_outline
        outline_c = pac_c
        fill_c = pac_c

        if self.capture:
            outline_c = team_c[index % 2]
            fill_c = ghost_c[index]
            width = pac_capture_outline

        return [circle(screen_point, pac_s * self.grid_size,
                       fill_c=fill_c, outline_c=outline_c,
                       end_coord=end_coord,
                       width=width)]

    #used for rotating pacman according to direction
    def get_end_coord(self, direction, position=(0, 0)):
        x, y = position
        coord = x - int(x) + y - int(y)
        width = 30 + 80 * math.sin(math.pi * coord)

        diff = width / 2
        if (direction == 'left'):
            end_coord = (180 + diff, 180 - diff)
        elif (direction == 'up'):
            end_coord = (90 + diff, 90 - diff)
        elif (direction == 'down'):
            end_coord = (270 + diff, 270 - diff)
        else:
            end_coord = (0 + diff, 0 - diff)
        return end_coord

    #for moving the pacman
    def move_pacman(self, position, direction, image):
        screen_coord = self.to_screen(position)
        end_coord = self.get_end_coord(direction, position)
        r = pac_s * self.grid_size
        move_circle(image[0], screen_coord, r, end_coord)
        refresh()

    #animation of pacman when moving from cell to cell
    def animate_pacman_movement(self, pacman, prevPacman, image):
        if self.frame_t < 0:
            print('Press any key to step forward, "q" to play')
            keys = wait_for_keys()
            if 'q' in keys:
                self.frame_t = 0.1
        if self.frame_t > 0.01 or self.frame_t < 0:
            start = time.time()
            fx, fy = self.get_coord(prevPacman)
            px, py = self.get_coord(pacman)
            frames = 4.0
            for i in range(1,int(frames) + 1):
                coord = px*i/frames + fx*(frames-i)/frames, py*i/frames + fy*(frames-i)/frames
                self.move_pacman(coord, self.get_dir(pacman), image)
                refresh()
                sleep(abs(self.frame_t) / frames)
        else:
            self.move_pacman(self.get_coord(pacman), self.get_dir(pacman), image)
        refresh()

    #retreiving the ghost color
    def get_ghost_color(self, ghost, ghost_index):
        if ghost.scared_timer > 0:
            return scare_c
        else:
            return ghost_c[ghost_index]

    #drawing the ghost
    def make_ghost(self, ghost, agent_index):
        coord = self.get_coord(ghost)
        dir = self.get_dir(ghost)
        (screen_x, screen_y) = (self.to_screen(coord))
        coords = []
        for (x, y) in ghost_dimensions:
            coords.append((x*self.grid_size*ghost_s + screen_x,
                           y*self.grid_size*ghost_s + screen_y))

        colour = self.get_ghost_color(ghost, agent_index)
        body = polygon(coords, colour, filled = 1)
        WHITE = format_color(1.0, 1.0, 1.0)
        BLACK = format_color(0.0, 0.0, 0.0)

        dx = 0
        dy = 0
        if dir == 'up':
            dy = -0.2
        if dir == 'down':
            dy = 0.2
        if dir == 'right':
            dx = 0.2
        if dir == 'left':
            dx = -0.2

        leftEye = circle((screen_x+self.grid_size*ghost_s*(-0.3+dx/1.5), screen_y -
                          self.grid_size*ghost_s*(0.3-dy/1.5)), self.grid_size*ghost_s*0.2, WHITE, WHITE)
        rightEye = circle((screen_x+self.grid_size*ghost_s*(0.3+dx/1.5), screen_y -
                           self.grid_size*ghost_s*(0.3-dy/1.5)), self.grid_size*ghost_s*0.2, WHITE, WHITE)
        leftPupil = circle((screen_x+self.grid_size*ghost_s*(-0.3+dx), screen_y -
                            self.grid_size*ghost_s*(0.3-dy)), self.grid_size*ghost_s*0.08, BLACK, BLACK)
        rightPupil = circle((screen_x+self.grid_size*ghost_s*(0.3+dx), screen_y -
                             self.grid_size*ghost_s*(0.3-dy)), self.grid_size*ghost_s*0.08, BLACK, BLACK)
        ghostImageParts = []
        ghostImageParts.append(body)
        ghostImageParts.append(leftEye)
        ghostImageParts.append(rightEye)
        ghostImageParts.append(leftPupil)
        ghostImageParts.append(rightPupil)

        # ghost_parts = []
        # ghost_parts.append(body)

        return ghostImageParts
    
    def moveEyes(self, pos, dir, eyes):
        (screen_x, screen_y) = (self.to_screen(pos))
        dx = 0
        dy = 0
        if dir == 'up':
            dy = -0.2
        if dir == 'down':
            dy = 0.2
        if dir == 'right':
            dx = 0.2
        if dir == 'left':
            dx = -0.2
        move_circle(eyes[0], (screen_x+self.grid_size*ghost_s*(-0.3+dx/1.5), screen_y -
                             self.grid_size*ghost_s*(0.3-dy/1.5)), self.grid_size*ghost_s*0.2)
        move_circle(eyes[1], (screen_x+self.grid_size*ghost_s*(0.3+dx/1.5), screen_y -
                             self.grid_size*ghost_s*(0.3-dy/1.5)), self.grid_size*ghost_s*0.2)
        move_circle(eyes[2], (screen_x+self.grid_size*ghost_s*(-0.3+dx), screen_y -
                             self.grid_size*ghost_s*(0.3-dy)), self.grid_size*ghost_s*0.08)
        move_circle(eyes[3], (screen_x+self.grid_size*ghost_s*(0.3+dx), screen_y -
                             self.grid_size*ghost_s*(0.3-dy)), self.grid_size*ghost_s*0.08)


    #moving the ghost
    def move_ghost(self, ghost, ghost_index, prevGhost, ghostImageParts):
        #animation of ghost movement
        old_x, old_y = self.to_screen(self.get_coord(prevGhost))
        new_x, new_y = self.to_screen(self.get_coord(ghost))
        diff = new_x - old_x, new_y - old_y

        for ghostImagePart in ghostImageParts:
            move_by(ghostImagePart, diff)
        refresh()

        if ghost.scared_timer > 0:
            color = scare_c #setting the color of scared state
        else:
            color = ghost_c[ghost_index]
        edit(ghostImageParts[0], ('fill', color), ('outline', color))
        self.moveEyes(self.get_coord(ghost),
                      self.get_dir(ghost), ghostImageParts[-4:])
        refresh()

    #get coords on the screen
    def get_coord(self, agentState):
        if agentState.location == None: return (-1000, -1000)
        return agentState.get_coord()

    #get action
    def get_dir(self, agentState):
        if agentState.location == None: return movement.STOP
        return agentState.location.get_dir()

    def finish(self):
        end_graphics() #utility function for ending the display

    #converting the point coords to to_screen
    def to_screen(self, point):
        (x, y) = point
        x = (x + 1)*self.grid_size
        y = (self.height - y)*self.grid_size
        return (x, y)
    
    def to_screen2(self, point):
        (x, y) = point
        #y = self.height - y
        x = (x + 1)*self.grid_size
        y = (self.height - y)*self.grid_size
        return (x, y)

    #drawing the walls from the wallMatrix
    def make_wall(self, wallMatrix):
        wall_color = wall_c
        for xNum, x in enumerate(wallMatrix):
            if self.capture and (xNum * 2) < wallMatrix.width:
                wall_color = team_c[0]
            if self.capture and (xNum * 2) >= wallMatrix.width:
                wall_color = team_c[1]
            for yNum, cell in enumerate(x):
                if cell: # There's a wall here
                    coord = (xNum, yNum)
                    screen = self.to_screen(coord)
                    screen2 = self.to_screen2(coord)

                    # draw each quadrant of the square based on adjacent walls
                    wis_wall = self.is_wall(xNum-1, yNum, wallMatrix)
                    eis_wall = self.is_wall(xNum+1, yNum, wallMatrix)
                    nis_wall = self.is_wall(xNum, yNum+1, wallMatrix)
                    sis_wall = self.is_wall(xNum, yNum-1, wallMatrix)
                    nwis_wall = self.is_wall(xNum-1, yNum+1, wallMatrix)
                    swis_wall = self.is_wall(xNum-1, yNum-1, wallMatrix)
                    neis_wall = self.is_wall(xNum+1, yNum+1, wallMatrix)
                    seis_wall = self.is_wall(xNum+1, yNum-1, wallMatrix)

                    # NE quadrant
                    if (not nis_wall) and (not eis_wall):
                        # inner circle
                        circle(screen2, wall_r * self.grid_size, 
                               wall_color, wall_color, (0,91), 'arc')
                    if (nis_wall) and (not eis_wall):
                        # vertical line
                        line(add(screen, (self.grid_size*wall_r, 0)), add(screen, 
                                                                          (self.grid_size*wall_r, self.grid_size*(-0.5)-1)), wall_color)
                    if (not nis_wall) and (eis_wall):
                        # horizontal line
                        line(add(screen, (0, self.grid_size*(-1)*wall_r)), add(screen, 
                                                                               (self.grid_size*0.5+1, self.grid_size*(-1)*wall_r)), wall_color)
                    if (nis_wall) and (eis_wall) and (not neis_wall):
                        # outer circle
                        circle(add(screen2, (self.grid_size*2*wall_r, self.grid_size*(-2)*wall_r)),
                               wall_r * self.grid_size-1, wall_color, wall_color, (180,271), 'arc')
                        line(add(screen, (self.grid_size*2*wall_r-1, self.grid_size*(-1)*wall_r)), 
                             add(screen, (self.grid_size*0.5+1, self.grid_size*(-1)*wall_r)), wall_color)
                        line(add(screen, (self.grid_size*wall_r, self.grid_size*(-2)*wall_r+1)), 
                             add(screen, (self.grid_size*wall_r, self.grid_size*(-0.5))), wall_color)

                    # NW quadrant
                    if (not nis_wall) and (not wis_wall):
                        # inner circle
                        circle(screen2, wall_r * self.grid_size, 
                               wall_color, wall_color, (90,181), 'arc')
                    if (nis_wall) and (not wis_wall):
                        # vertical line
                        line(add(screen, (self.grid_size*(-1)*wall_r, 0)), add(screen, 
                                                                               (self.grid_size*(-1)*wall_r, self.grid_size*(-0.5)-1)), wall_color)
                    if (not nis_wall) and (wis_wall):
                        # horizontal line
                        line(add(screen, (0, self.grid_size*(-1)*wall_r)), add(screen, 
                                                                               (self.grid_size*(-0.5)-1, self.grid_size*(-1)*wall_r)), wall_color)
                    if (nis_wall) and (wis_wall) and (not nwis_wall):
                        # outer circle
                        circle(add(screen2, (self.grid_size*(-2)*wall_r, self.grid_size*(-2)*wall_r)),
                                wall_r * self.grid_size-1, wall_color, wall_color, (270,361), 'arc')
                        line(add(screen, (self.grid_size*(-2)*wall_r+1, self.grid_size*(-1)*wall_r)), 
                             add(screen, (self.grid_size*(-0.5), self.grid_size*(-1)*wall_r)), wall_color)
                        line(add(screen, (self.grid_size*(-1)*wall_r, self.grid_size*(-2)*wall_r+1)), 
                             add(screen, (self.grid_size*(-1)*wall_r, self.grid_size*(-0.5))), wall_color)

                    # SE quadrant
                    if (not sis_wall) and (not eis_wall):
                        # inner circle
                        circle(screen2, wall_r * self.grid_size, 
                               wall_color, wall_color, (270,361), 'arc')
                    if (sis_wall) and (not eis_wall):
                        # vertical line
                        line(add(screen, (self.grid_size*wall_r, 0)), add(screen, 
                                                                          (self.grid_size*wall_r, self.grid_size*(0.5)+1)), wall_color)
                    if (not sis_wall) and (eis_wall):
                        # horizontal line
                        line(add(screen, (0, self.grid_size*(1)*wall_r)), add(screen, 
                                                                              (self.grid_size*0.5+1, self.grid_size*(1)*wall_r)), wall_color)
                    if (sis_wall) and (eis_wall) and (not seis_wall):
                        # outer circle
                        circle(add(screen2, (self.grid_size*2*wall_r, self.grid_size*(2)*wall_r)), 
                               wall_r * self.grid_size-1, wall_color, wall_color, (90,181), 'arc')
                        line(add(screen, (self.grid_size*2*wall_r-1, self.grid_size*(1)*wall_r)), 
                             add(screen, (self.grid_size*0.5, self.grid_size*(1)*wall_r)), wall_color)
                        line(add(screen, (self.grid_size*wall_r, self.grid_size*(2)*wall_r-1)), 
                             add(screen, (self.grid_size*wall_r, self.grid_size*(0.5))), wall_color)

                    # SW quadrant
                    if (not sis_wall) and (not wis_wall):
                        # inner circle
                        circle(screen2, wall_r * self.grid_size, 
                               wall_color, wall_color, (180,271), 'arc')
                    if (sis_wall) and (not wis_wall):
                        # vertical line
                        line(add(screen, (self.grid_size*(-1)*wall_r, 0)), add(screen, 
                                                                               (self.grid_size*(-1)*wall_r, self.grid_size*(0.5)+1)), wall_color)
                    if (not sis_wall) and (wis_wall):
                        # horizontal line
                        line(add(screen, (0, self.grid_size*(1)*wall_r)), add(screen, 
                                                                              (self.grid_size*(-0.5)-1, self.grid_size*(1)*wall_r)), wall_color)
                    if (sis_wall) and (wis_wall) and (not swis_wall):
                        # outer circle
                        circle(add(screen2, (self.grid_size*(-2)*wall_r, self.grid_size*(2)*wall_r)), 
                               wall_r * self.grid_size-1, wall_color, wall_color, (0,91), 'arc')
                        line(add(screen, (self.grid_size*(-2)*wall_r+1, self.grid_size*(1)*wall_r)), 
                             add(screen, (self.grid_size*(-0.5), self.grid_size*(1)*wall_r)), wall_color)
                        line(add(screen, (self.grid_size*(-1)*wall_r, self.grid_size*(2)*wall_r-1)), 
                             add(screen, (self.grid_size*(-1)*wall_r, self.grid_size*(0.5))), wall_color)

    #checking if the coords given are of walls or not
    def is_wall(self, x, y, walls):
        if x < 0 or y < 0:
            return False
        if x >= walls.width or y >= walls.height:
            return False
        return walls[x][y]

    #drawing the coin on the maze
    def make_coin(self, coin_grid):
        coin_img = []
        color = coin_c
        for xNum, x in enumerate(coin_grid):
            if self.capture and (xNum * 2) <= coin_grid.width:
                color = team_c[0]
            if self.capture and (xNum * 2) > coin_grid.width:
                color = team_c[1]
            img_row = []
            coin_img.append(img_row)
            for yNum, cell in enumerate(x):
                if cell: # There's coin here
                    screen = self.to_screen((xNum, yNum ))
                    dot = circle(screen,
                                  coin_s * self.grid_size,
                                  outline_c = color, fill_c = color,
                                  width = 1)
                    img_row.append(dot)
                else:
                    img_row.append(None)
        return coin_img

    #drawing bcoin on the maze
    def make_big_coin(self, big_coin):
        big_food_img = {}
        for bigcoin in big_coin:
            ( screen_x, screen_y ) = self.to_screen(bigcoin)
            dot = circle( (screen_x, screen_y),
                              big_coin_s * self.grid_size,
                              outline_c = big_coin_c,
                              fill_c = big_coin_c,
                              width = 1)
            big_food_img[bigcoin] = dot
        return big_food_img

    #removing the coin from the maze
    def rem_coin(self, cell, coin_img ):
        x, y = cell
        remove_from_screen(coin_img[x][y])

    #removing the bcoin from the maze
    def remove_big_food(self, cell, big_food_img ):
        x, y = cell
        remove_from_screen(big_food_img[(x, y)])

    def drawExpandedCells(self, cells):
        """
        Draws an overlay of expanded grid positions for search agents
        """
        n = float(len(cells))
        baseColor = [1.0, 0.0, 0.0]
        self.clearExpandedCells()
        self.expandedCells = []
        for k, cell in enumerate(cells):
            screenPos = self.to_screen(cell)
            cellColor = format_color(
                *[(n-k) * c * .5 / n + .25 for c in baseColor])
            block = square(screenPos,
                           0.5 * self.grid_size,
                           color=cellColor,
                           filled=1, behind=2)
            self.expandedCells.append(block)
            if self.frame_t < 0:
                refresh()

    def clearExpandedCells(self):
        if 'expandedCells' in dir(self) and len(self.expandedCells) > 0:
            for cell in self.expandedCells:
                remove_from_screen(cell)

    def updateDistributions(self, distributions):
        "Draws an agent's belief distributions"
        # copy all distributions so we don't change their state
        distributions = [x.copy() for x in distributions]
        if self.distributionImages == None:
            self.drawDistributions(self.previousState)
        for x in range(len(self.distributionImages)):
            for y in range(len(self.distributionImages[0])):
                image = self.distributionImages[x][y]
                weights = [dist[(x, y)] for dist in distributions]

                if sum(weights) != 0:
                    pass
                # Fog of war
                color = [0.0, 0.0, 0.0]
                colors = ghost_vect_c[1:]  # With Pacman
                if self.capture:
                    colors = ghost_vect_c
                for weight, gcolor in zip(weights, colors):
                    color = [min(1.0, c + 0.95 * g * weight ** .3)
                             for c, g in zip(color, gcolor)]
                changeColor(image, format_color(*color))
        refresh()


class FirstPersonPacmanGraphics(pac_graphic):
    def __init__(self, zoom=1.0, showGhosts=True, capture=False, frame_t=0):
        pac_graphic.__init__(self, zoom, frame_t=frame_t)
        self.showGhosts = showGhosts
        self.capture = capture

    def initialize(self, state, isBlue=False):

        self.isBlue = isBlue
        pac_graphic.start_graphic(self, state)
        # Initialize distribution images
        walls = state.maze.walls
        dist = []
        self.maze = state.maze

        # Draw the rest
        self.distributionImages = None  # initialize lazily
        self.make_static_obj(state)
        self.make_agent_obj(state)

        # Information
        self.previousState = state

    def lookAhead(self, config, state):
        if config.get_dir() == 'Stop':
            return
        else:
            pass
            # Draw relevant ghosts
            allGhosts = state.getGhostStates()
            visibleGhosts = state.getVisibleGhosts()
            for i, ghost in enumerate(allGhosts):
                if ghost in visibleGhosts:
                    self.make_ghost(ghost, i)
                else:
                    self.currentGhostImages[i] = None

    def get_ghost_color(self, ghost, ghostIndex):
        return ghost_c[ghostIndex]

    def get_coord(self, ghostState):
        if not self.showGhosts and not ghostState.is_pac and ghostState.get_coord()[1] > 1:
            return (-1000, -1000)
        else:
            return pac_graphic.get_coord(self, ghostState)


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


# Saving graphical output
# -----------------------
# Note: to make an animated gif from this postscript output, try the command:
# convert -delay 7 -loop 1 -compress lzw -layers optimize frame* out.gif
# convert is part of imagemagick (freeware)

SAVE_POSTSCRIPT = False
POSTSCRIPT_OUTPUT_DIR = 'frames'
FRAME_NUMBER = 0
import os


def saveFrame():
    "Saves the current graphical output as a postscript file"
    global SAVE_POSTSCRIPT, FRAME_NUMBER, POSTSCRIPT_OUTPUT_DIR
    if not SAVE_POSTSCRIPT:
        return
    if not os.path.exists(POSTSCRIPT_OUTPUT_DIR):
        os.mkdir(POSTSCRIPT_OUTPUT_DIR)
    name = os.path.join(POSTSCRIPT_OUTPUT_DIR, 'frame_%08d.ps' % FRAME_NUMBER)
    FRAME_NUMBER += 1
    writePostscript(name)  # writes the current canvas