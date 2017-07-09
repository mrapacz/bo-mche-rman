import curses


class ConsoleRenderer(object):
    EMPTY_TILE = ' '
    UNKNOWN_TILE = '?'

    def __init__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)
        self.stdscr.scrollok(True)
        self.stdscr.nodelay(True)  # set getch() non-blocking
        self._clear_screen()

    def _clear_screen(self):
        self.stdscr.clear()

    def render(self, board):
        self._clear_screen()
        self.print(board)

    def end(self):
        curses.endwin()

    def print(self, text):
        self._clear_screen()
        self.stdscr.addstr(str(text))
