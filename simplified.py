import curses
import time


# settings
HEIGHT = 32
WIDTH = 64

EMPTY_TILE = ' '
TILES_MAP = {
    'flame': '~',
    'block': '+',
    'player': 'o',
    'bomb': 'x'
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


class Player(object):
    pass


class Flame(object):
    pass


class Bomb(object):
    pass


def initialize_board():
    board = [None]*HEIGHT
    for line in board:
        line.append([None]*WIDTH)

    for y in range(HEIGHT):
        board[y][0] = board[y][WIDTH] = 'block'

    for x in range(WIDTH):
        board[0][x] = board[HEIGHT][x] = 'block'

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


def handle_keys():
    pass


def sleep(measured_time):
    pass


def run_game_loop(initial_state, board):
    is_finished = False
    game_state = initial_state

    while not is_finished:
        current_time = time.time()

        handle_keys()
        update(game_state, board)
        display(board)

        sleep(current_time)



initial_state = {
    'players': [],
    'bombs': [],
    'flames': [],
}

run_game_loop()