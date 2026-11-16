from pico2d import *


WIDTH, HEIGHT = 800, 450
FPS = 60
GRAVITY = 1500
PLAYER_SPEED = 250
JUMP_SPEED = 560
GROUND_Y = 58

FONT_PATH = "C:/Windows/Fonts/malgun.ttf"

PLATFORMS = {
    "현실": [(285, 430, 145), (505, 650, 220)],
    "그림자": [(205, 350, 125), (405, 555, 180), (590, 735, 260)],
}


class Player:
    def __init__(self):
        self.x = 100
        self.y = GROUND_Y
        self.vy = 0
        self.direction = 1
        self.on_ground = True
        self.frame = 0
        self.anim_time = 0

    def update(self, dt, keys, platforms):
        moving = 0
        if SDLK_LEFT in keys or SDLK_a in keys:
            moving -= 1
        if SDLK_RIGHT in keys or SDLK_d in keys:
            moving += 1
        if moving:
            self.direction = moving
            self.x += moving * PLAYER_SPEED * dt
        self.x = max(22, min(WIDTH - 22, self.x))

        old_y = self.y
        self.vy -= GRAVITY * dt
        self.y += self.vy * dt
        self.on_ground = False

        if self.vy <= 0:
            for left, right, top in [(0, WIDTH, GROUND_Y), *platforms]:
                overlaps = self.x + 18 > left and self.x - 18 < right
                crossed_top = old_y >= top and self.y <= top
                if overlaps and crossed_top:
                    self.y = top
                    self.vy = 0
                    self.on_ground = True
                    break

        if moving:
            self.anim_time += dt
            self.frame = int(self.anim_time * 10) % 8
        else:
            self.frame = 0

    def jump(self):
        if self.on_ground:
            self.vy = JUMP_SPEED
            self.on_ground = False

    def draw(self):
        x, y = self.x, self.y
        facing = self.direction
        shirt = (246, 202, 112) if self.frame == 0 else (246, 185, 90)
        draw_circle(x, y + 44, 13, 43, 74, 91, filled=True)
        draw_rectangle(x - 11, y + 6, x + 11, y + 34, *shirt, filled=True)
        draw_rectangle(x - 20, y + 27, x + 20, y + 33, 54, 105, 78, filled=True)
        draw_line(x + facing * 10, y + 27, x + facing * 22, y + 12, 244, 194, 139)
        draw_line(x - facing * 10, y + 27, x - facing * 18, y + 15, 244, 194, 139)
        step = 5 if self.frame % 2 else -5
        draw_line(x - 5, y + 7, x - 8 + step, y - 2, 42, 54, 72)
        draw_line(x + 5, y + 7, x + 8 - step, y - 2, 42, 54, 72)
        draw_rectangle(x - 15 + step, y - 5, x - 4 + step, y, 35, 40, 54, filled=True)
        draw_rectangle(x + 4 - step, y - 5, x + 15 - step, y, 35, 40, 54, filled=True)


class ShadowBoundaryDemo:
    def __init__(self):
        self.font = load_font(str(FONT_PATH), 18)
        self.title_font = load_font(str(FONT_PATH), 30)
        self.reset()

    def reset(self):
        self.player = Player()
        self.box_x = 340
        self.box_y = GROUND_Y + 18
        self.box_vx = 0
        self.box_vy = 0
        self.world_index = 0
        self.keys = set()
        self.won = False
        self.running = True

    @property
    def world_name(self):
        return ("현실", "그림자")[self.world_index]

    @property
    def platforms(self):
        return PLATFORMS[self.world_name]

    @property
    def switch_on(self):
        return abs(self.box_x - 600) < 38 and self.box_y <= GROUND_Y + 20

    def handle_events(self):
        for event in get_events():
            if event.type == SDL_QUIT:
                self.running = False
            elif event.type == SDL_KEYDOWN:
                self.keys.add(event.key)
                if event.key == SDLK_ESCAPE:
                    self.running = False
                elif event.key == SDLK_SPACE or event.key == SDLK_UP:
                    self.player.jump()
                elif event.key == SDLK_z:
                    self.world_index = 1 - self.world_index
                elif event.key == SDLK_r:
                    self.reset()
                elif event.key == SDLK_RETURN and self.won:
                    self.reset()
            elif event.type == SDL_KEYUP:
                self.keys.discard(event.key)

    def update(self, dt):
        if self.won:
            return

        old_box_y = self.box_y
        pushing = SDLK_e in self.keys
        player_near_box = abs(self.player.x - self.box_x) < 58
        push_direction = 1 if self.player.x < self.box_x else -1
        old_player_x = self.player.x

        self.player.update(dt, set() if pushing and player_near_box else self.keys, self.platforms)

        if not pushing and abs(self.player.y - (self.box_y - 18)) < 12:
            if old_player_x < self.box_x and self.player.x + 18 > self.box_x - 18:
                self.player.x = self.box_x - 36
            elif old_player_x > self.box_x and self.player.x - 18 < self.box_x + 18:
                self.player.x = self.box_x + 36

        if pushing and player_near_box:
            self.player.direction = push_direction
            self.box_vx += push_direction * 720 * dt
        self.box_vx *= 0.80
        self.box_vx = max(-220, min(220, self.box_vx))
        self.box_x += self.box_vx * dt
        self.box_x = max(25, min(WIDTH - 25, self.box_x))

        self.box_vy -= GRAVITY * dt
        self.box_y += self.box_vy * dt
        if self.box_y - 18 < GROUND_Y:
            self.box_y = GROUND_Y + 18
            self.box_vy = 0
        else:
            for left, right, top in self.platforms:
                overlaps = self.box_x + 18 > left and self.box_x - 18 < right
                crossed_top = old_box_y - 18 >= top and self.box_y - 18 <= top
                if overlaps and crossed_top and self.box_vy <= 0:
                    self.box_y = top + 18
                    self.box_vy = 0
                    break

        if pushing and player_near_box:
            self.player.x = self.box_x - push_direction * 38

        if self.switch_on and self.player.x > 690:
            self.won = True

    def draw_world(self):
        if self.world_index == 0:
            draw_rectangle(0, 0, WIDTH, HEIGHT, 174, 218, 245, filled=True)
            draw_rectangle(0, 58, WIDTH, HEIGHT, 104, 170, 114, filled=True)
            draw_rectangle(0, 48, WIDTH, 63, 94, 126, 77, filled=True)
            for x in range(0, WIDTH, 18):
                draw_line(x, 58, x + 7, 68, 127, 185, 94)
            platform_color = (96, 123, 112)
            accent = (245, 204, 100)
        else:
            draw_rectangle(0, 0, WIDTH, HEIGHT, 30, 34, 64, filled=True)
            draw_rectangle(0, 58, WIDTH, HEIGHT, 65, 53, 105, filled=True)
            draw_rectangle(0, 48, WIDTH, 63, 77, 67, 126, filled=True)
            platform_color = (145, 105, 207)
            accent = (165, 226, 255)

        for left, right, top in self.platforms:
            draw_rectangle(left, top, right, top + 18, *platform_color, filled=True)
            draw_rectangle(left, top + 14, right, top + 19, *accent, filled=True)

        plate_color = (92, 238, 170) if self.switch_on else (231, 125, 88)
        draw_rectangle(574, GROUND_Y, 626, GROUND_Y + 8, *plate_color, filled=True)

        door_color = (92, 238, 170) if self.switch_on else (90, 83, 106)
        draw_rectangle(714, GROUND_Y, 766, 142, *door_color, filled=True)
        draw_rectangle(724, GROUND_Y + 12, 756, 130, 38, 42, 63, filled=True)

    def draw(self):
        clear_canvas()
        self.draw_world()

        draw_rectangle(
            self.box_x - 18,
            self.box_y - 18,
            self.box_x + 18,
            self.box_y + 18,
            198,
            132,
            74,
            filled=True,
        )
        draw_rectangle(
            self.box_x - 12,
            self.box_y - 12,
            self.box_x + 12,
            self.box_y + 12,
            225,
            178,
            112,
        )
        self.player.draw()

        world_color = (38, 51, 72) if self.world_index == 0 else (235, 231, 255)
        self.title_font.draw(24, HEIGHT - 42, "그림자 경계  |  " + self.world_name, world_color)
        self.font.draw(24, HEIGHT - 72, "← → 이동   SPACE 점프   Z 세계 전환   E 상자 밀기   R 재시작", world_color)
        switch_text = "스위치: 작동!" if self.switch_on else "스위치: 상자를 오른쪽으로 밀어 작동"
        self.font.draw(24, HEIGHT - 101, switch_text, world_color)

        if self.won:
            draw_rectangle(100, 160, 700, 300, 20, 24, 42, 235, filled=True)
            self.title_font.draw(272, 245, "스테이지 클리어!", (255, 255, 255))
            self.font.draw(263, 205, "ENTER 키를 눌러 다시 플레이", (210, 220, 245))

        update_canvas()

    def run(self):
        while self.running:
            self.handle_events()
            self.update(1 / FPS)
            self.draw()
            delay(1 / FPS)


def main():
    open_canvas(WIDTH, HEIGHT)
    game = ShadowBoundaryDemo()
    game.run()
    close_canvas()


if __name__ == "__main__":
    main()
