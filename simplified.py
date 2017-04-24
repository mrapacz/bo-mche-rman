import curses
import time


# settings
FPS = 30
HEIGHT = 32
WIDTH = 64

EMPTY_TILE = ' '
TILES_MAP = {
    'flame': '~',
    'block': '+',
    'player': 'o',
    'bomb': 'x',
}


# configure terminal
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)
stdscr.scrollok(True)
stdscr.nodelay(True)  # set getch() non-blocking


# override default print() function
def print(text):
    stdscr.addstr(str(text))
    stdscr.refresh()


def clear():
    stdscr.clear()


class MapObject(object):

    def __init__(self):
        self.x = 0
        self.y = 0


class Player(MapObject):

    def __init__(self):
        super().__init__()

        self.x_velocity = 1
        self.y_velocity = 1

    def move(self, x, y):
        new_x, new_y = self.x + x, self.y + y
        # TODO: collision check

        self.x, self.y = new_x, new_y


class Flame(MapObject):
    pass


class Bomb(MapObject):
    pass


def initialize_board():
    board = [[] for _ in range(HEIGHT)]

    for line in board:
        for _ in range(WIDTH):
            line.append(None)

    for y in range(HEIGHT):
        board[y][0] = board[y][WIDTH-1] = 'block'

    for x in range(WIDTH):
        board[0][x] = board[HEIGHT-1][x] = 'block'

    return board


def display(board):
    output = []

    for y in range(HEIGHT):
        for x in range(WIDTH):
            tile = board[y][x]
            character = TILES_MAP[tile] if tile else EMPTY_TILE
            output.append(character)

        output.append("\n")

    stdscr.clear()
    print("".join(output))


def update(game_state, board):
    pass


def move():
    pass


def handle_keys(game_state):
    pass


def run_game_loop(initial_state, board):
    is_finished = False
    game_state = initial_state
    last_frame_time = 0

    while not is_finished:
        current_time = time.time()

        handle_keys(game_state)
        update(game_state, board)
        display(board)

        sleep_time = 1.0/FPS - (current_time - last_frame_time)
        if sleep_time > 0:
            time.sleep(sleep_time)
        last_frame_time = current_time


initial_state = {
    'players': [],
    'bombs': [],
    'flames': [],
}

board = initialize_board()

run_game_loop(initial_state, board)
