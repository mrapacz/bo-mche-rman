from asyncio import sleep
from sys import stdin, exit

from PodSixNet.Connection import connection, ConnectionListener

from _thread import *

from clientgame import ClientGame
from consolerenderer import ConsoleRenderer


class Client(ConnectionListener):
    def __init__(self, host, port):
        self.in_game = False
        self.Connect((host, port))

        self.set_nickname()

    def start_new_game(self):
        self.set_room()

        self.console = ConsoleRenderer()
        self.client_game = ClientGame(self.console)
        self.in_game = True

    def loop(self):
        key_pressed = self.client_game.getch()
        if key_pressed:
            connection.Send({"action": "input", "key": key_pressed})

        connection.Pump()
        c.Pump()

    # hackerrank.com
    # udemy.com
    # coursera.org


    @staticmethod
    def set_nickname():
        nickname = input("Enter your nickname:\n")
        connection.Send({"action": "nickname", "nickname": nickname})

    @staticmethod
    def set_room():
        room = input("Enter room number:\n")
        connection.Send({"action": "join_room", "room": room})

    # Network event/message callbacks

    def Network_display_board(self, data):
        board = data['board']
        self.console.render(board)

    def Network_joinedroom(self, data):
        self.console.print("Successfully joined room number " + data['room_number'] + '\n')
        # todo optionally -> you are going to play against

    def Network_declinedroom(self, data):
        self.console.print("Declined: Could not join room number {} - it's already full.\n".format(data['room_number']))
        self.set_room()

    # game-specific section
    def Network_gameprelude(self, data):
        self.console.print("The game is going to begin in 3 seconds\n")

    def Network_gamestart(self, data):
        self.console.print("The game is going to begin now...\n")

    def Network_gameresult(self, data):
        self.console.end()
        print(
            "The game has finished. {} won the game.".format(data['winner']))

        sleep(3)
        self.in_game = False

    def Network_gamestate(self, data):
        self.console.print(data['state'])

    # built in stuff

    def Network_connected(self, data):
        self.console.print("Successfully connected to the server.\n")

    def Network_error(self, data):
        print('error:', data['error'][1])
        connection.Close()
        self.console.end()

    def Network_disconnected(self, data):
        print('Server disconnected')
        self.console.end()
        exit()


host = '127.0.0.1'
port = 31425
c = Client(host, port)
while True:
    try:
        if c.in_game:
            c.loop()
        else:
            c.start_new_game()
    except KeyboardInterrupt:
        c.console.end()
        break
