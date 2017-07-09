import curses


class ClientGame(object):
    key_mapping = {
        curses.KEY_UP: 'up',
        curses.KEY_DOWN: 'down',
        curses.KEY_LEFT: 'left',
        curses.KEY_RIGHT: 'right',
        ord('x'): 'x',
    }

    def __init__(self, console):
        self.console = console

    def getch(self):
        key_pressed = self.console.stdscr.getch()
        return self.key_mapping.get(key_pressed, '')
