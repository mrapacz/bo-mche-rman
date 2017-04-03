import curses
import time
import random

from collections import defaultdict, namedtuple

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)
stdscr.scrollok(True)
stdscr.nodelay(True)  # set getch() non-blocking


def print(text):
    stdscr.addstr(str(text))


def get_unique_sequence():
    seed = random.getrandbits(32)
    while True:
       yield seed
       seed += 1

unique_sequence = get_unique_sequence()

Position = namedtuple('Position', ['x', 'y'])
ExplosionRange = namedtuple('ExplosionRange', ['up', 'right', 'down', 'left'])


class RemovableMixin(object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_removed = False
        self.time_limit = 10
        self.start_time = time.time()

    def _before_removal(self):
        pass

    def update(self):
        current_time = time.time()

        if current_time - self.start_time > self.time_limit:
            self._before_removal()

            self.position = Position(None, None)
            self.is_removed = True


class MapObject(object):

    OBJECT_NAME = 'object'

    def __init__(self, position):
        self.position = position
        self.id = "{}-{}".format(self.OBJECT_NAME, str(next(unique_sequence)))

    def update(self):
        pass


class Flame(RemovableMixin,
            MapObject):

    OBJECT_NAME = 'flame'

    def __init__(self, position):
        super().__init__(position)
        self.time_limit = 5


class Bomb(RemovableMixin,
           MapObject):

    OBJECT_NAME = 'bomb'

    def __init__(self, position, create_explosion_callback):
        super().__init__(position)
        self.time_limit = 3
        self.start_time = time.time()

        self.create_explosion = create_explosion_callback
        self.explosion_range = ExplosionRange(5, 5, 10, 10)

    def _before_removal(self):
        self.create_explosion(self.position, self.explosion_range)


class Block(MapObject):

    OBJECT_NAME = 'block'


class Player(MapObject):

    OBJECT_NAME = 'player'

    def __init__(self, position, map):
        super().__init__(position)
        self.x_speed = 1
        self.y_speed = 1
        self.map = map

    def _move(self, x, y):
        new_position = Position(self.position.x + x, self.position.y + y)

        tile_objects = self.map.get_tile_objects(new_position)

        if (Block.OBJECT_NAME in tile_objects
            or new_position.x < 0 or new_position.x > self.map.width-1
                or new_position.y < 0 or new_position.y > self.map.height-1):
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


class Map(object):

    def __init__(self, renderer, width, height):
        self.renderer = renderer
        self.width = width
        self.height = height
        self.object_positions = {}
        self.tiles = defaultdict(lambda: defaultdict(list))

    def add_object(self, map_object):
        x, y = map_object.position

        self.tiles[y][x].append(map_object.OBJECT_NAME)
        self.object_positions[map_object.id] = map_object.position

    def update_object(self, map_object):
        old_x, old_y = self.object_positions[map_object.id]
        self.tiles[old_y][old_x].remove(map_object.OBJECT_NAME)

        x, y = map_object.position

        if not x or not y:
            del self.object_positions[map_object.id]
            return

        self.object_positions[map_object.id] = map_object.position
        self.tiles[y][x].append(map_object.OBJECT_NAME)

    def get_tile_objects(self, position):
        x, y = position
        return self.tiles[y][x]

    def render(self):
        self.renderer.render(self.tiles)


class ConsoleRenderer(object):

    EMPTY_TILE = ' '

    TILE_MAP = {
        Player.OBJECT_NAME: 'O',
        Block.OBJECT_NAME: '+',
        Flame.OBJECT_NAME: '~',
        Bomb.OBJECT_NAME: 'X',
    }

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def _clear_screen(self):
        stdscr.clear()

    def _get_buffered_output(self, tiles):
        output = []

        for y in range(self.height):
            for x in range(self.width):
                tile = tiles[y][x]

                if tile:
                    output.append(self.TILE_MAP.get(tile[0], self.EMPTY_TILE))
                else:
                    output.append(self.EMPTY_TILE)
            output.append("\n")

        return "".join(output)

    def render(self, tiles):
        output = self._get_buffered_output(tiles)
        self._clear_screen()
        print(output)


class Game(object):

    FPS = 30

    WIDTH = 128
    HEIGHT = 32

    def __init__(self):
        self.renderer = ConsoleRenderer(self.WIDTH, self.HEIGHT)
        self.map = Map(self.renderer, self.WIDTH, self.HEIGHT)
        self.players = []
        self.bombs = []
        self.explosions = []
        self.blocks = []
        self.flames = []

    def _get_player_key_mapping(self, player):
        def plant_bomb():
            bomb = Bomb(player.position, self._create_explosion)
            self.bombs.append(bomb)
            self.map.add_object(bomb)

        return {
            curses.KEY_UP: player.move_up,
            curses.KEY_DOWN: player.move_down,
            curses.KEY_LEFT: player.move_left,
            curses.KEY_RIGHT: player.move_right,
            ord('x'): plant_bomb,
        }

    def _get_second_player_key_mapping(self, player):
        def plant_bomb():
            bomb = Bomb(player.position, self._create_explosion)
            self.bombs.append(bomb)
            self.map.add_object(bomb)

        return {
            ord('w'): player.move_up,
            ord('s'): player.move_down,
            ord('a'): player.move_left,
            ord('d'): player.move_right,
        }

    def _initialize_blocks(self):
        self.blocks = [Block(Position(x, 0)) for x in range(self.WIDTH)]
        self.blocks += [Block(Position(0, y)) for y in range(self.HEIGHT)]
        self.blocks += [Block(Position(x, self.HEIGHT-1)) for x in range(self.WIDTH)]
        self.blocks += [Block(Position(self.WIDTH-1, y)) for y in range(self.HEIGHT)]
        self.blocks += [Block(Position(x, y)) for y in range(2, self.HEIGHT-3, 4)
                        for x in range(2, self.WIDTH-3, 2)]

        for block in self.blocks:
            self.map.add_object(block)

    def _create_explosion(self, position, explosion_range):
        up_flames = [Flame(Position(position.x, position.y - y)) for y in range(explosion_range.up) if position.y - y > 0]
        right_flames = [Flame(Position(position.x + x, position.y)) for x in range(explosion_range.right) if position.x + x < self.WIDTH-1]
        down_flames = [Flame(Position(position.x, position.y + y)) for y in range(explosion_range.down) if position.y + y < self.HEIGHT-1]
        left_flames = [Flame(Position(position.x - x, position.y)) for x in range(explosion_range.left) if position.x - x > 0]

        flames = up_flames + right_flames + down_flames + left_flames

        for flame in flames:
            self.map.add_object(flame)

        self.flames += flames

    def _update(self):
        self.bombs = [bomb for bomb in self.bombs if not bomb.is_removed]
        self.flames = [flame for flame in self.flames if not flame.is_removed]

        game_objects = self.bombs + self.flames + self.players

        for game_object in game_objects:
            game_object.update()
            self.map.update_object(game_object)

    def _run_game_loop(self):
        first_player = Player(Position(3, 4), self.map)
        first_player_key_mapping = self._get_player_key_mapping(first_player)

        second_player = Player(Position(5, 6), self.map)
        second_player_key_mapping = self._get_second_player_key_mapping(second_player)

        self.players.append(first_player)
        self.map.add_object(first_player)
        self.players.append(second_player)
        self.map.add_object(second_player)

        self._initialize_blocks()

        last_frame_time = 0

        while True:
            current_time = time.time()
            key_pressed = stdscr.getch()

            try:
                first_player_key_mapping[key_pressed]()
            except KeyError:
                pass

            try:
                second_player_key_mapping[key_pressed]()
            except KeyError:
                pass

            self._update()

            self.map.render()

            sleep_time = 1.0/self.FPS - (current_time - last_frame_time)

            last_frame_time = current_time
            print(sleep_time)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def run(self):
        self._run_game_loop()

try:
    game = Game()
    game.run()
finally:
    curses.endwin()


# handle players key press
# check if these moves are feasable
# move players, plant bombs

# update() all game objects (players, bombs, explosions)

# bombs and explosions are automatically removed, create new explosions

# get players collisions, if colliding with flame mark end of the game

# render map
