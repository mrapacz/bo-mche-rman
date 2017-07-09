import threading
from time import sleep

from game import Game


class Room:
    def __init__(self, server, room_number):
        print("Launching a room")
        self.player_count = 0
        self.players = []
        self.game_state = 0
        self.game = Game()
        self.server = server
        self.room_number = room_number

    def AddPlayer(self, player):
        if self.player_count not in (0, 1):
            # the room must be full
            return False

        self.players.append(player)
        self.player_count += 1
        if self.player_count == 2:
            thread = threading.Thread(target=self.run, args=())
            thread.start()
        return True

    def DeletePlayer(self, player):
        if player in self.players:
            self.players.remove(player)
            self.player_count -= 1
            self.game_state = 0

    def run(self):
        print("Running the game.")
        sleep(1)
        self.notify_game_prelude()
        sleep(3)
        print("The game has begun")

        self.game.start([player.nickname for player in self.players])
        self.notify_game_start()

        while self.game.is_running:
            self.game.process_loop_once()
            self.notify_game_state({
                'board': self.game.rendered_board,
            })

        self.notify_game_result(list(self.game.players.keys())[0])

    # Game -> Player
    def message_players(self, action, data):
        self.server.SendMessageToPlayers(self.players, action, data)

    def notify_game_prelude(self):
        self.message_players("gameprelude", {})

    def notify_game_start(self):
        self.game_state = True
        self.message_players("gamestart", {})

    def notify_game_state(self, state):
        """
        :param state: a map that will later be rendered by the Client
        :return: None
        """
        self.message_players("display_board", state)

    def notify_game_result(self, winner):
        self.game_state = False
        self.message_players("gameresult", {'winner': winner, 'loser': ''})
        self.server.DeleteRoom(self.room_number)

    # Player -> Game
    def Input(self, player, key):
        """
        :param player: Client
        :param key: 
        :return: 
        """
        print("Player {} has pressed key {}".format(player.nickname, key))
        self.game.on_player_key_press(player.nickname, key)
