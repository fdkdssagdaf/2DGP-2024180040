import math
import random

from pico2d import *
import py_trees


SCREEN_WIDTH = 960
SCREEN_HEIGHT = 768
SOURCE_WIDTH = 1280
SOURCE_HEIGHT = 1024
BALL_COUNT = 14
BOY_SPEED = 8
ZOMBIE_SPEED = 2
BOY_DETECTION_RANGE = 150
BOY_STOP_DISTANCE = 40
FOOTBALL_TARGET_RANGE = 180
IDLE_RIGHT_ROW, IDLE_LEFT_ROW = 300, 200
RUN_RIGHT_ROW, RUN_LEFT_ROW = 100, 0
ZOMBIE_FRAME_WIDTH = 430
ZOMBIE_FRAME_HEIGHT = 519
ZOMBIE_FRAME_COUNT = 10
ZOMBIE_DRAW_WIDTH = 120
ZOMBIE_DRAW_HEIGHT = 145
PATROL_POINTS_IMAGE = (
    (43, 274),
    (1118, 274),
    (1050, 494),
    (575, 804),
    (235, 991),
    (575, 804),
    (1050, 494),
    (1118, 274),
)


def image_point_to_screen(point):
    x, y = point
    return (
        round(x * SCREEN_WIDTH / SOURCE_WIDTH),
        round((SOURCE_HEIGHT - y) * SCREEN_HEIGHT / SOURCE_HEIGHT),
    )


PATROL_POINTS = tuple(image_point_to_screen(point) for point in PATROL_POINTS_IMAGE)


def draw_target_markers(blackboard, marker):
    for target_x, target_y in blackboard.target_positions.values():
        marker.draw(target_x, target_y)


class Boy:
    def __init__(self):
        self.image = load_image('animation_sheet.png')
        self.x, self.y = 80, SCREEN_HEIGHT - 100
        self.frame = 0
        self.facing = 1
        self.moving = False
        self.keys = set()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            self.keys.add(event.key)
        elif event.type == SDL_KEYUP:
            self.keys.discard(event.key)

    def update(self):
        move_x = int(SDLK_RIGHT in self.keys) - int(SDLK_LEFT in self.keys)
        move_y = int(SDLK_UP in self.keys) - int(SDLK_DOWN in self.keys)
        if move_x and move_y:
            move_x *= 0.70710678
            move_y *= 0.70710678

        next_x = round(max(50, min(SCREEN_WIDTH - 50, self.x + move_x * BOY_SPEED)))
        next_y = round(max(80, min(SCREEN_HEIGHT - 50, self.y + move_y * BOY_SPEED)))
        self.moving = next_x != self.x or next_y != self.y
        if next_x != self.x:
            self.facing = 1 if next_x > self.x else -1
        self.x, self.y = next_x, next_y
        self.frame = (self.frame + 1) % 8

    def get_bb(self):
        return self.x - 35, self.y - 45, self.x + 35, self.y + 45

    def draw(self):
        if self.moving:
            row = RUN_RIGHT_ROW if self.facing > 0 else RUN_LEFT_ROW
        else:
            row = IDLE_RIGHT_ROW if self.facing > 0 else IDLE_LEFT_ROW
        self.image.clip_draw(self.frame * 100, row, 100, 100, self.x, self.y)


class SetRandomBallTarget(py_trees.behaviour.Behaviour):
    def __init__(self, zombie, zombies, footballs, blackboard):
        super().__init__(name=f"Set Target Location {zombie.name}")
        self.zombie = zombie
        self.zombies = zombies
        self.footballs = footballs
        self.blackboard = blackboard

    def update(self):
        reserved_ids = {
            other.target_ball.ball_id
            for other in self.zombies
            if other is not self.zombie
            and other.target_ball is not None
            and other.target_ball in self.footballs
        }
        candidates = [
            football
            for football in self.footballs
            if football.ball_id not in reserved_ids
            and math.hypot(
                football.x - self.zombie.x,
                football.y - self.zombie.y,
            ) <= FOOTBALL_TARGET_RANGE
        ]
        if not candidates:
            self.zombie.target_ball = None
            targets = dict(self.blackboard.target_positions)
            targets.pop(self.zombie.name, None)
            self.blackboard.target_positions = targets
            return py_trees.common.Status.FAILURE

        football = random.choice(candidates)
        self.zombie.target_ball = football
        targets = dict(self.blackboard.target_positions)
        targets[self.zombie.name] = (football.x, football.y)
        self.blackboard.target_positions = targets
        return py_trees.common.Status.SUCCESS


class MoveToTargetBall(py_trees.behaviour.Behaviour):
    def __init__(self, zombie, footballs, blackboard):
        super().__init__(name=f"Move To Target Location {zombie.name}")
        self.zombie = zombie
        self.footballs = footballs
        self.blackboard = blackboard

    def update(self):
        football = self.zombie.target_ball
        if football is None or football not in self.footballs:
            return py_trees.common.Status.SUCCESS

        target = self.blackboard.target_positions.get(self.zombie.name)
        if target is None:
            return py_trees.common.Status.FAILURE

        target_x, target_y = target
        if collide(self.zombie, football):
            return py_trees.common.Status.SUCCESS

        dx = target_x - self.zombie.x
        dy = target_y - self.zombie.y
        distance = math.hypot(dx, dy)

        if distance <= ZOMBIE_SPEED:
            self.zombie.x = target_x
            self.zombie.y = target_y
            return py_trees.common.Status.SUCCESS

        self.zombie.x += dx / distance * ZOMBIE_SPEED
        self.zombie.y += dy / distance * ZOMBIE_SPEED
        return py_trees.common.Status.RUNNING


class MoveToPatrolPoint(py_trees.behaviour.Behaviour):
    def __init__(self, zombie, point, index, blackboard):
        super().__init__(name=f"Move To Patrol Point {index}")
        self.zombie = zombie
        self.point = point
        self.blackboard = blackboard

    def update(self):
        targets = dict(self.blackboard.target_positions)
        if targets.get(self.zombie.name) != self.point:
            targets[self.zombie.name] = self.point
            self.blackboard.target_positions = targets

        target_x, target_y = self.point
        dx = target_x - self.zombie.x
        dy = target_y - self.zombie.y
        distance = math.hypot(dx, dy)
        if distance <= ZOMBIE_SPEED:
            self.zombie.x, self.zombie.y = self.point
            return py_trees.common.Status.SUCCESS

        self.zombie.x += dx / distance * ZOMBIE_SPEED
        self.zombie.y += dy / distance * ZOMBIE_SPEED
        return py_trees.common.Status.RUNNING


class RemoveTargetBall(py_trees.behaviour.Behaviour):
    def __init__(self, zombie, footballs, blackboard):
        super().__init__(name=f"Remove Target Football {zombie.name}")
        self.zombie = zombie
        self.footballs = footballs
        self.blackboard = blackboard

    def update(self):
        football = self.zombie.target_ball
        if football is not None and football in self.footballs:
            self.footballs.remove(football)
            self.zombie.eaten_count += 1
            self.blackboard.eaten_count += 1

        targets = dict(self.blackboard.target_positions)
        targets.pop(self.zombie.name, None)
        self.blackboard.target_positions = targets
        self.zombie.target_ball = None
        return py_trees.common.Status.SUCCESS


class BoyNearby(py_trees.behaviour.Behaviour):
    def __init__(self, zombie, boy):
        super().__init__(name="소년이 근처에 있는가?")
        self.zombie = zombie
        self.boy = boy

    def update(self):
        distance = math.hypot(
            self.boy.x - self.zombie.x,
            self.boy.y - self.zombie.y,
        )
        if distance <= BOY_DETECTION_RANGE:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class MoveToBoy(py_trees.behaviour.Behaviour):
    def __init__(self, zombie, boy):
        super().__init__(name="소년한테 가기")
        self.zombie = zombie
        self.boy = boy

    def update(self):
        dx = self.boy.x - self.zombie.x
        dy = self.boy.y - self.zombie.y
        distance = math.hypot(dx, dy)
        if distance <= BOY_STOP_DISTANCE:
            return py_trees.common.Status.SUCCESS

        distance_to_move = min(ZOMBIE_SPEED, distance - BOY_STOP_DISTANCE)
        self.zombie.x += dx / distance * distance_to_move
        self.zombie.y += dy / distance * distance_to_move
        return py_trees.common.Status.RUNNING


class Zombie:
    def __init__(self, name, x, y, image):
        self.name = name
        self.image = image
        self.x, self.y = x, y
        self.frame = 0
        self.target_ball = None
        self.eaten_count = 0

    def update(self):
        self.frame = (self.frame + 1) % ZOMBIE_FRAME_COUNT

    def get_bb(self):
        return self.x - 35, self.y - 45, self.x + 35, self.y + 45

    def draw(self, font):
        self.image.clip_draw(
            self.frame * ZOMBIE_FRAME_WIDTH,
            0,
            ZOMBIE_FRAME_WIDTH,
            ZOMBIE_FRAME_HEIGHT,
            self.x,
            self.y,
            ZOMBIE_DRAW_WIDTH,
            ZOMBIE_DRAW_HEIGHT,
        )
        draw_rectangle(*self.get_bb(), 255, 0, 0, 255)
        font.draw(
            self.x - 8,
            self.y + ZOMBIE_DRAW_HEIGHT // 2 + 8,
            str(self.eaten_count),
            (30, 100, 255),
        )


class Football:
    def __init__(self, ball_id, x, y, image):
        self.ball_id = ball_id
        self.x, self.y = x, y
        self.image = image

    def get_bb(self):
        return self.x - 20, self.y - 20, self.x + 20, self.y + 20

    def draw(self):
        self.image.draw(self.x, self.y)


def scatter_footballs(image):
    positions = []
    while len(positions) < BALL_COUNT:
        x = random.randint(45, SCREEN_WIDTH - 45)
        y = random.randint(45, SCREEN_HEIGHT - 45)
        if x < 220 and y > SCREEN_HEIGHT - 220:
            continue
        if x > SCREEN_WIDTH - 390 and y > SCREEN_HEIGHT - 190:
            continue
        if any(math.hypot(x - px, y - py) < 60 for px, py in positions):
            continue
        positions.append((x, y))
    return [
        Football(ball_id, x, y, image)
        for ball_id, (x, y) in enumerate(positions)
    ]


def draw_blackboard(font, blackboard, zombies):
    left = SCREEN_WIDTH - 380
    top = SCREEN_HEIGHT - 12
    bottom = top - 158
    draw_rectangle(left, bottom, SCREEN_WIDTH - 12, top, 30, 35, 45, 225, True)
    font.draw(left + 14, top - 30, "BLACKBOARD", (255, 255, 255))
    font.draw(
        left + 14,
        top - 58,
        f"Football eaten: {blackboard.eaten_count}",
        (40, 130, 255),
    )
    boy_x, boy_y = blackboard.boy_position
    font.draw(
        left + 14,
        top - 112,
        f"Boy position: ({boy_x}, {boy_y})",
        (245, 245, 245),
    )
    for index, zombie in enumerate(zombies):
        target = blackboard.target_positions.get(zombie.name)
        coordinates = "none" if target is None else f"({target[0]}, {target[1]})"
        font.draw(
            left + 14,
            top - 86 - index * 26,
            f"{zombie.name}: {coordinates}",
            (245, 245, 245),
        )


def collide(a, b):
    left_a, bottom_a, right_a, top_a = a.get_bb()
    left_b, bottom_b, right_b, top_b = b.get_bb()
    return left_a < right_b and right_a > left_b and bottom_a < top_b and top_a > bottom_b


open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)
background = load_image('../LEC10_HandlingInputs/TUK_GROUND.png')
target_marker = load_image('../LEC10_HandlingInputs/hand_arrow.png')
football_image = load_image('ball41x41.png')
zombie_image = load_image('zombie_run_animation.png')
font = load_font(r'C:\Windows\Fonts\arial.ttf', 20)
boy = Boy()
footballs = scatter_footballs(football_image)
zombies = [Zombie("Zombie 1", 650, 100, zombie_image)]
blackboard = py_trees.blackboard.Client(name="GameBlackboard")
blackboard.register_key(
    key="target_positions", access=py_trees.common.Access.WRITE
)
blackboard.register_key(key="eaten_count", access=py_trees.common.Access.WRITE)
blackboard.register_key(key="boy_position", access=py_trees.common.Access.WRITE)
blackboard.target_positions = {}
blackboard.eaten_count = 0
blackboard.boy_position = (boy.x, boy.y)
hud_blackboard = py_trees.blackboard.Client(name="BlackboardDisplay")
hud_blackboard.register_key(
    key="target_positions", access=py_trees.common.Access.READ
)
hud_blackboard.register_key(
    key="eaten_count", access=py_trees.common.Access.READ
)
hud_blackboard.register_key(
    key="boy_position", access=py_trees.common.Access.READ
)
zombie_trees = []
for index, zombie in enumerate(zombies, start=1):
    target_reader = py_trees.blackboard.Client(name=f"ZombieTargetReader-{index}")
    target_reader.register_key(
        key="target_positions", access=py_trees.common.Access.READ
    )
    tracking_sequence = py_trees.composites.Sequence(
        name="소년추적",
        memory=False,
        children=[
            BoyNearby(zombie, boy),
            MoveToBoy(zombie, boy),
        ],
    )
    target_location_sequence = py_trees.composites.Sequence(
        name=f"{zombie.name} Target Location Sequence",
        memory=True,
        children=[
            SetRandomBallTarget(zombie, zombies, footballs, blackboard),
            MoveToTargetBall(zombie, footballs, target_reader),
        ],
    )
    football_sequence = py_trees.composites.Sequence(
        name=f"{zombie.name} Football Sequence",
        memory=True,
        children=[
            target_location_sequence,
            RemoveTargetBall(zombie, footballs, blackboard),
        ],
    )
    patrol_sequence = py_trees.composites.Sequence(
        name=f"{zombie.name} Patrol Sequence",
        memory=True,
        children=[
            MoveToPatrolPoint(zombie, point, point_index, blackboard)
            for point_index, point in enumerate(PATROL_POINTS, start=1)
        ],
    )
    root = py_trees.composites.Selector(
        name=f"{zombie.name} Root Mode",
        memory=False,
        children=[tracking_sequence, football_sequence, patrol_sequence],
    )
    zombie_trees.append(py_trees.trees.BehaviourTree(root))
running = True

while running:
    events = get_events()
    for event in events:
        if event.type in (SDL_KEYDOWN, SDL_KEYUP):
            boy.handle_event(event)
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                running = False

    boy.update()
    blackboard.boy_position = (boy.x, boy.y)
    for behaviour_tree in zombie_trees:
        behaviour_tree.tick()
    for zombie in zombies:
        zombie.update()

    clear_canvas()
    background.draw(
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2,
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
    )
    for football in footballs:
        football.draw()
    boy.draw()
    draw_rectangle(*boy.get_bb(), 255, 0, 0, 255)
    for zombie in zombies:
        zombie.draw(font)
    draw_target_markers(hud_blackboard, target_marker)
    draw_blackboard(font, hud_blackboard, zombies)
    update_canvas()
    delay(0.05)

close_canvas()
