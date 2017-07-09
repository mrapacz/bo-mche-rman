import time


class BoardObject(object):

    OBJECT_NAME = 'object'

    def __init__(self, position):
        self.position = position

    def update(self):
        pass

    def remove(self):
        self.position = None


class Flame(BoardObject):

    OBJECT_NAME = 'flame'

    def __init__(self, position):
        super().__init__(position)
        self.frames_until_removal = 50

    def update(self):
        self.frames_until_removal -= 1
        if self.frames_until_removal <= 0:
            self.remove()


class Bomb(BoardObject):

    OBJECT_NAME = 'bomb'
    EXPLOSION_RANGE = (5, 5, 10, 10)

    def __init__(self, position, board):
        super().__init__(position)
        self.frames_until_removal = 90
        self.board = board

    def create_flames(self):
        bomb_x, bomb_y = self.position
        up, down, left, right = self.EXPLOSION_RANGE

        up_flames = [Flame((bomb_x, bomb_y - y)) for y in range(up) if bomb_y - y > 0]
        right_flames = [Flame((bomb_x + x, bomb_y)) for x in range(right) if bomb_x + x < self.board.width-1]
        down_flames = [Flame((bomb_x, bomb_y + y)) for y in range(down) if bomb_y + y < self.board.height-1]
        left_flames = [Flame((bomb_x - x, bomb_y)) for x in range(left) if bomb_x - x > 0]

        return up_flames + right_flames + down_flames + left_flames

    def update(self):
        self.frames_until_removal -= 1
        if self.frames_until_removal <= 0:
            flames = self.create_flames()
            self.remove()
            return flames


class Block(BoardObject):

    OBJECT_NAME = 'block'


class Player(BoardObject):

    OBJECT_NAME = 'player'

    def __init__(self, position, board):
        super().__init__(position)
        self.x_speed = 1
        self.y_speed = 1
        self.board = board
        self.planting_bomb = False

    def _move(self, x, y):
        player_x, player_y = self.position
        new_x, new_y = player_x + x, player_y + y
        new_position = (new_x, new_y)

        tile_objects = self.board.get_tile_objects(new_position)

        if (Block.OBJECT_NAME in tile_objects
            or new_x < 0 or new_x > self.board.width-1
                or new_y < 0 or new_y > self.board.height-1):
            return

        self.position = new_position

    def move_right(self):
        self._move(self.x_speed, 0)

    def move_left(self):
        self._move(-self.x_speed, 0)

    def move_up(self):
        self._move(0, -self.y_speed)

    def move_down(self):
        self._move(0, self.y_speed)

    def plant_bomb(self):
        self.planting_bomb = True

    def update(self):
        if self.planting_bomb:
            self.planting_bomb = False
            return [Bomb(self.position, self.board)]


class Board(object):

    def __init__(self, renderer, width, height):
        self.renderer = renderer
        self.width = width
        self.height = height
        self.tiles = Board.initialize_tiles(width, height)

    @classmethod
    def initialize_tiles(cls, width, height):
        tiles = [[] for _ in range(height)]

        for line in tiles:
            for _ in range(width):
                line.append([])

        return tiles

    def clear(self):
        self.tiles = Board.initialize_tiles(self.width, self.height)

    def add_object(self, board_object):
        x, y = board_object.position
        self.tiles[y][x].append(board_object.OBJECT_NAME)

    def get_tile_objects(self, position):
        x, y = position
        return self.tiles[y][x]

    def render(self):
        return self.renderer.render(self.tiles)


class StringRenderer(object):
    EMPTY_TILE = ' '
    UNKNOWN_TILE = '?'

    TILE_MAP = {
        Player.OBJECT_NAME: 'O',
        Block.OBJECT_NAME: '+',
        Flame.OBJECT_NAME: '~',
        Bomb.OBJECT_NAME: 'X',
    }

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def _get_buffered_output(self, tiles):
        output = []

        for y in range(self.height):
            for x in range(self.width):
                tile = tiles[y][x]

                if tile:
                    output.append(self.TILE_MAP.get(tile[0], self.UNKNOWN_TILE))
                else:
                    output.append(self.EMPTY_TILE)
            output.append("\n")

        return "".join(output)

    def render(self, tiles):
        return self._get_buffered_output(tiles)


class Game(object):

    FPS = 30
    WIDTH = 64
    HEIGHT = 32

    KEY_ACTION_MAPPING = {
        'up': Player.move_up,
        'down': Player.move_down,
        'left': Player.move_left,
        'right': Player.move_right,
        'x': Player.plant_bomb,
    }

    def __init__(self):
        self.renderer = StringRenderer(self.WIDTH, self.HEIGHT)
        self.board = Board(self.renderer, self.WIDTH, self.HEIGHT)
        self.players = {}
        self.objects = []
        self.key_presses = []
        self.is_running = False
        self.last_frame_time = 0
        self.rendered_board = ''

    def update(self):
        self.board.clear()

        new_objects = []
        for obj in self.objects:
            objects = obj.update()
            if objects:
                new_objects += objects

        self.objects += new_objects
        self.objects = [obj for obj in self.objects if obj.position]

        for obj in self.objects:
            self.board.add_object(obj)

    def remove_dead_players(self):
        removed_players = []

        for nickname, player in self.players.items():
            tiles = self.board.get_tile_objects(player.position)
            if Flame.OBJECT_NAME in tiles:
                player.remove()
                removed_players.append(nickname)

        for nickname in removed_players:
            del self.players[nickname]

        if len(self.players) == 1:
            self.is_running = False

    def process_loop_once(self):
        if not self.is_running:
            return

        current_time = time.time()

        self.handle_key_presses()
        self.update()
        self.remove_dead_players()
        self.rendered_board = self.board.render()

        sleep_time = 1.0/self.FPS - (current_time - self.last_frame_time)
        self.last_frame_time = current_time
        if sleep_time > 0:
            time.sleep(sleep_time)

    def on_player_key_press(self, nickname, key_name):
        self.key_presses.append((nickname, key_name))

    def handle_key_presses(self):
        for nickname, key_name in self.key_presses:
            player = self.players.get(nickname)

            if not player:
                continue

            action = self.KEY_ACTION_MAPPING[key_name]
            action(player)

        self.key_presses = []

    def _initialize_blocks(self):
        blocks = [Block((x, 0)) for x in range(self.WIDTH)]
        blocks += [Block((0, y)) for y in range(self.HEIGHT)]
        blocks += [Block((x, self.HEIGHT-1)) for x in range(self.WIDTH)]
        blocks += [Block((self.WIDTH-1, y)) for y in range(self.HEIGHT)]
        blocks += [Block((x, y)) for y in range(2, self.HEIGHT-3, 4)
                   for x in range(2, self.WIDTH-3, 2)]
        return blocks

    def _initialize_players(self, nicknames):
        return {nickname: Player((3, 4), self.board)
                for nickname in nicknames}

    def start(self, nicknames):
        self.players = self._initialize_players(nicknames)
        blocks = self._initialize_blocks()

        self.objects = blocks + list(self.players.values())
        self.is_running = True

