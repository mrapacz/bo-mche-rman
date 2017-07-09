import sys
from collections import defaultdict
from time import sleep, localtime
from weakref import WeakKeyDictionary

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
from room import Room


class ClientChannel(Channel):
    """
    This is the server representation of a single connected client.
    """

    def __init__(self, *args, **kwargs):
        self.nickname = "anonymous"
        self.room_number = None
        Channel.__init__(self, *args, **kwargs)

    def Close(self):
        self._server.DelPlayer(self)

    def Network_message(self, data):
        self._server.SendToAll({"action": "message", "message": data['message'], "who": self.nickname})

    def Network_nickname(self, data):
        self.nickname = data['nickname']

    def Network_join_room(self, data):
        room = data['room']
        self._server.AddPlayerToRoom(self, room)

    def Network_input(self, data):
        if self.room_number is not None:
            self._server.PassInputToRoom(self, data)


class BombermanServer(Server):
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.players = WeakKeyDictionary()
        self.channelClass = ClientChannel
        # Each room should contain a dict of (room_number -> Room)"""
        self.rooms = defaultdict(lambda: Room())

        print('Server launched')

    def Connected(self, channel, addr):
        self.AddPlayer(channel)

    def AddPlayerToRoom(self, player, room_number):
        if room_number not in self.rooms:
            self.rooms[room_number] = Room(self, room_number)
        if self.rooms[room_number].AddPlayer(player):
            print("Granting access for {} to join room {}".format(player, room_number))
            player.room_number = room_number
            player.Send({'action': 'joinedroom', 'room_number': room_number})

        else:
            player.Send({'action': 'declinedroom', 'room_number': room_number})
            print("Declining access")

    def AddPlayer(self, player):
        print("New Player joined: " + str(player.addr))
        self.players[player] = True
        print("players", [p.nickname for p in self.players])

    def PassInputToRoom(self, player, data):
        room = self.rooms[player.room_number]
        if room.game_state:
            key = data['key']
            self.rooms[player.room_number].Input(player, key)

    def SendMessageToPlayers(self, players, action, data):
        message = {'action': action}
        message.update(data)
        # print(message)
        for player in players:
            player.Send(message)

    def DelPlayer(self, player):
        print("Deleting Player" + str(player.addr))
        del self.players[player]



    def DeleteRoom(self, room_number):
        for player in self.rooms[room_number].players:
            if player.room_number == room_number:
                player.room_number = None
        del self.rooms[room_number]

    def Launch(self):
        while True:
            self.Pump()


host = "localhost"
port = 31425
s = BombermanServer(localaddr=(host, port))
s.Launch()

