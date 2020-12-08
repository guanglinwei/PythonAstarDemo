import sys
import math
import os
import asyncio

try:
    import pygame
    import tkinter as tk
except:
    import install_requirements
    import pygame
    import tkinter as tk


# colors
WHITE = (255, 255, 255)
RED = (255, 102, 102)
GREEN = (102, 255, 102)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 128, 0)
GRAY = (128, 128, 128)
LIGHTGRAY = (221, 221, 221)
BLACK = (0, 0, 0)

screen_w = 800
screen_h = 800
cols = 50
rows = 50
tile_w = screen_w // cols
tile_h = screen_h // rows
grid = [0 for i in range(rows)]
for i in range(cols):
    grid[i] = [0 for i in range(rows)]

#if the help menu is open, don't open another one
global tk_win_exists

# (x, y)
global last_mouse_point
global update_speed

class tile:
    def __init__(self, x, y, col = WHITE):
        self.x = x
        self.y = y
        self.g = 0
        self.h = 0
        self.f = 0
        self.adj = []
        self.parent = None
        self.color = col

    def get_children(self):
        ret = []

        check_diagonals = True

        # get tiles surrounding this one that can be reached.
        # we have to check that diagonals are reachable, without going through walls
        # ex: check the tile to the right. if it is walkable, add it.
        # This also means that means moving ur (up + right) and dr (down + right) is not moving through a wall. Mark these diagonals as available
        # Then, check the available diagonals to see if they are valid, add them if so
        ur = False
        dr = False
        dl = False
        ul = False

        if is_walkable_tile(self.x + 1, self.y):
            ret.append(grid[self.x + 1][self.y])
            ur = True
            dr = True
        if is_walkable_tile(self.x - 1, self.y):
            ret.append(grid[self.x - 1][self.y])
            ul = True
            dl = True
        if is_walkable_tile(self.x, self.y + 1):
            ret.append(grid[self.x][self.y + 1])
            # remember +y = down
            dr = True
            dl = True
        if is_walkable_tile(self.x, self.y - 1):
            ret.append(grid[self.x][self.y - 1])
            ur = True
            ul = True

        if not check_diagonals:
            return ret

        if ur and is_walkable_tile(self.x + 1, self.y - 1):
            ret.append(grid[self.x + 1][self.y - 1])
        if dr and is_walkable_tile(self.x + 1, self.y + 1):
            ret.append(grid[self.x + 1][self.y + 1])
        if dl and is_walkable_tile(self.x - 1, self.y + 1):
            ret.append(grid[self.x - 1][self.y + 1])
        if ul and is_walkable_tile(self.x - 1, self.y - 1):
            ret.append(grid[self.x - 1][self.y - 1])

        return ret

    def set_empty(self):
        self.color = WHITE
    def is_empty(self):
        return self.color == WHITE
    def set_start(self):
        self.color = ORANGE
    def is_start(self):
        return self.color == ORANGE
    def set_end(self):
        self.color = BLUE
    def is_end(self):
        return self.color == BLUE
    def set_wall(self):
        self.color = BLACK
    def is_wall(self):
        return self.color == BLACK
    def set_open(self):
        self.color = GREEN
    def set_closed(self):
        self.color = RED
    def set_path(self):
        self.color = MAGENTA




display = pygame.display.set_mode((screen_w, screen_h))

# A*
def astar(ctx):
    global update_speed
    update_speed = 1.0
    
    if ctx.has_path_now:
        clear_open_closed()

    ctx.has_path_now = False

    start = ctx.current_start
    end = ctx.current_end

    start.g = 0
    start.h = heu(start, end)

    # init open/closed sets, add start to open
    openSet = []
    closedSet = []
    openSet.append(start)

    # while openSet is not empty
    while(len(openSet) > 0):
        start.set_start()
        end.set_end()

        # find the tile in openSet with the lowest f score
        lowestInd = 0
        for i in range(len(openSet)):
            if openSet[i].f < openSet[lowestInd].f:
                lowestInd = i

        # remove the lowest f score tile from the openSet and add it to the closedSet
        current = openSet.pop(lowestInd)
        closedSet.append(current)
        current.set_closed()

        # are we at the end? if so show path
        if(current == end):
            update_speed = 1.0
        # if(end in closedSet):
            ctx.has_path_now = True
            end.g = current.g + heu(current, end)
            # path = []
            c = current.parent
            end.set_end()
            while c is not None:
                # path.append((c.x, c.y))
                c.set_path()

                #color effect
                c_r, c_g, c_b = c.color
                c_r = int(c_r * (.4 + (.6 * c.g / end.g)))
                c.color = (c_r, c_g, c_b)

                c = c.parent
                yield

            start.set_start()
            ctx.receive_inputs = True
            return True

        # increase speed of animation   
        update_speed += 0.01

        # tiles around current
        children = current.get_children()

        # number of children that were actually added into the openSet. if less than 0, do not yield and waste time
        good_children = 0

        for i in range(len(children)):
            child = children[i]

            will_cont = False

            #if in closedSet, go to next
            for n in closedSet:
                if child.x == n.x and child.y == n.y:
                    will_cont = True
                    break

            if will_cont:
                continue

            # if in openSet, check if new f score would be better, if so, replace that tile with this child
            for n in openSet:
                if child == n:
                    will_cont = True
                    if current.g + heu(current, child) + child.h < child.f:
                    # if current.g < child.g:
                        child.g = current.g + heu(current, child)
                        child.f = child.g + child.h
                        child.parent = current
                        break


            if will_cont:
                continue

            # set values
            child.g = current.g + heu(current, child)
            child.h = heu(child, end)
            child.f = child.g + child.h
            child.parent = current

            openSet.append(child)
            child.set_open()
            good_children+=1


        if good_children > 0:
            yield

    ctx.receive_inputs = True
    return False


# Heuristic dist between two tiles
def heu(t1, t2):
    temp = math.sqrt((t1.x - t2.x) ** 2 + (t1.y - t2.y) ** 2)
    # temp = int(abs(t1.x - t2.x) + abs(t1.y - t2.y))
    return temp

    # dx = abs(t1.x - t2.x)
    # dy = abs(t1.y - t2.y)
    #
    # if dx > dy:
    #     return dx + .4 * dy # (1.4 * dy) + dx - dy
    # # else
    # return dy + .4 * dx


# has wall at tile or invalid
def is_walkable_tile(x, y):
    return not(x < 0 or y < 0 or x >= cols or y >= rows or grid[x][y].is_wall())


# handles input
INPUT_LMB = 0
INPUT_RMB = 1
INPUT_SPACE = 2
INPUT_KEY_R = 3
def handle_input(button, ctx):
    if tk_win_exists: 
        return
        
    # place tiles
    if button == INPUT_LMB:
        global last_mouse_point

        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_x = int(mouse_x // tile_w)
        mouse_y = int(mouse_y // tile_h)

        if ctx.current_start is None or ctx.current_end is None or last_mouse_point[0] == -1:
            pass
        
        else:
            draw_line_between(mouse_x, mouse_y, last_mouse_point[0], last_mouse_point[1], BLACK)

        last_mouse_point = (mouse_x, mouse_y)

        mouse_tile = grid[mouse_x][mouse_y]

        # if the tile clicked is empty, then set it to start/end/wall
        if mouse_tile.is_empty():
            if(ctx.current_start is None):
                ctx.current_start = mouse_tile
                mouse_tile.set_start()
                return
            if(ctx.current_end is None):
                ctx.current_end = mouse_tile
                mouse_tile.set_end()
                return
            mouse_tile.set_wall()

        return

    # delete tile
    if button == INPUT_RMB:
        grid[0][1].color = RED
        draw_line_between(2, 32, 16, 2, BLACK)
        draw_line_between(5, 48, 22, 42, GREEN)
        draw_line_between(4, 4, 16, 2, BLACK)
        return
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_x = int(mouse_x // tile_w)
        mouse_y = int(mouse_y // tile_h)

        mouse_tile = grid[mouse_x][mouse_y]

        # if deleting the start/end tiles, make them none. Then set the tile to empty
        if mouse_tile.is_start():
            ctx.current_start = None
        if mouse_tile.is_end():
            ctx.current_end = None
        mouse_tile.set_empty()

    # start alg
    if button == INPUT_SPACE:
        if ctx.current_start is None or ctx.current_end is None:
            return

        ctx.receive_inputs = False
        # asyncio.run(astar(ctx))
        ctx.astar_iterator = astar(ctx)
        return

    # erase whole board
    if button == INPUT_KEY_R:
        setup_grid(ctx)
        return


def draw_line_between(x1, y1, x2, y2, col):
    # vertical
    if x1 == x2:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            attempt_draw_color(x1, y, col)
        return

    # horiz
    if y1 == y2:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            attempt_draw_color(x, y1, col)
        return

    # swap so point 1 is to left of point 2
    if x1 > x2:
        tx, ty = x1, y1
        x1, y1 = x2, y2
        x2, y2 = tx, ty

    dx = float(x2 - x1)
    dy = float(y2 - y1)
    steep = abs(dy) > dx
    
    derr = abs(dx / dy) if steep else abs(dy / dx)
    err = 0.0

    # |slope| > 1
    if steep:
        x = x1
        r = range(min(y1, y2), max(y1, y2) + 1)
        if y1 > y2:
            r = reversed(r)
        
        for y in r:
            attempt_draw_color(x, y, col)
            err += derr
            if err >= 0.5:
                x += (1 if dx > 0 else -1)
                err -= 1.0

    # |slope| < 1
    else:
        y = y1
        for x in range(min(x1, x2), max(x1, x2) + 1):
            attempt_draw_color(x, y, col)
            err += derr
            if err >= 0.5:
                y += (1 if dy > 0 else -1)
                err -= 1.0


def attempt_draw_color(x, y, col):
    if x in range(len(grid)) and y in range(len(grid[0])):
        if not (grid[x][y].is_start() or grid[x][y].is_end()):
            grid[x][y].color = col


def setup_grid(ctx):
    ctx.current_start = None
    ctx.current_end = None
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            grid[x][y] = tile(x, y)
            grid[x][y].set_empty()
            grid[x][y].g = float("inf")
            grid[x][y].f = float("inf")

def clear_open_closed():
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            t = grid[x][y]
            t.g = float("inf")
            t.f = float("inf")
            if t.is_start() or t.is_end() or t.is_wall():
                continue
            t.set_empty()

def redraw_screen():
    # clear
    display.fill(WHITE)

    # draw tiles and grid lines
    for i in range(rows):
        for j in range(cols):
            pygame.draw.line(display, LIGHTGRAY, (j * tile_w, 0), (j * tile_w, screen_h))

            t = grid[i][j]
            pygame.draw.rect(display, t.color, (t.x * tile_w + 1, t.y * tile_h + 1, tile_w - 1, tile_h - 1))
        pygame.draw.line(display, LIGHTGRAY, (0, i * tile_h), (screen_w, i * tile_h))

    pygame.display.update()


class ctx:
    def __init__(self):
        self.current_start = None
        self.current_end = None

        # can receive inputs besides quit? turned off when pathfinding
        self.receive_inputs = True

        # iterator for astar(ctx)
        self.astar_iterator = None

        # is there a path now
        self.has_path_now = False


def main():
    global last_mouse_point
    last_mouse_point = (-1, -1)
    global update_speed
    update_speed = 1.0

    app_ctx = ctx()

    setup_grid(app_ctx)

    while True:
        # global update_speed
        for i in range(int(update_speed)):
            if app_ctx.astar_iterator is not None:
                try:
                    next(app_ctx.astar_iterator)
                except StopIteration:
                    app_ctx.astar_iterator = None

        redraw_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            # still actually receive the reset input. This will stop the algorithm
            if not app_ctx.receive_inputs:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    app_ctx.astar_iterator = None
                    clear_open_closed()
                    app_ctx.receive_inputs = True
                continue

            if pygame.mouse.get_pressed()[0]:
                handle_input(INPUT_LMB, app_ctx)
            else:
                # last_mouse_point = (-1, -1)
                if pygame.mouse.get_pressed()[2]:
                    handle_input(INPUT_RMB, app_ctx)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    handle_input(INPUT_SPACE, app_ctx)
                elif event.key == pygame.K_r:
                    handle_input(INPUT_KEY_R, app_ctx)
                elif event.key == pygame.K_h:
                    if not tk_win_exists:
                        tkwind = create_tk_window()

        if not pygame.mouse.get_pressed()[0]:
            last_mouse_point = (-1, -1)
            

# explanation window
def confirm_tk_window(win):
    # win.quit()
    global tk_win_exists
    tk_win_exists = False
    win.destroy()
    
def create_tk_window():
    global tk_win_exists
    tk_win_exists = True
    
    win = tk.Tk()
    win.geometry("280x200")
    win.title("Astar Pathfinding Python Demo")
    labels = [
        tk.Label(win, text="Press H to open this window again"),
        tk.Label(win, text="Left Click to place the start tile (orange)"),
        tk.Label(win, text="Left Click again to place the end tile (blue)"),
        tk.Label(win, text="If you have a start and end tile, Left Click make walls"),
        tk.Label(win, text="Right Click to delete a tile"),
        tk.Label(win, text="Press Space to start pathfinding"),
        tk.Label(win, text="Press R to restart (This can be done at any time)")
    ]
    submit = tk.Button(win, text="OK", command=lambda: confirm_tk_window(win))
    submit.grid(column=1, row=len(labels)+2)
    for i in range(len(labels)):
        labels[i].grid(column=1, row=i+1)

    win.update()
    tk.mainloop()
    return win


tkwind = create_tk_window()


pygame.init()

main()
