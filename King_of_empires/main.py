from King_of_empires.config import *


#  Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.lives = 4
        self.speed = 1
        self.player_channel = pygame.mixer.Channel(1)
        self.player_channel.set_volume(0.5)
        self.shot_pos = {(1, 0): 0, (1, -1): 45, (0, -1): 90, (-1, -1): 135, (-1, 0): 180, (-1, 1): 225, (0, 1): 270,
                         (1, 1): 315}
        self.effects = {"triple_shot": 0, "multi_shot": 0, "speed_increase": 0}
        self.x_value, self.y_value = None, None
        self.shot_pos_x, self.shot_pos_y = None, None
        self.movement_pos_x, self.movement_pos_y = None, None
        self.counter = 0
        self.image = player_images["player"]
        self.rect = self.image.get_rect().move(tile_size * self.pos_x - (tile_size - self.image.get_width()),
                                               tile_size * self.pos_y - (tile_size - self.image.get_height()))

    def check_move(self, x_value, y_value):
        self.speed = 1
        if self.effects["speed_increase"] != 0:
            self.speed = 1.5
        if (x_value or y_value) and 0 <= self.pos_x + x_value < level_width and \
                0 <= self.pos_y + y_value < level_height and \
                map_matrix[self.pos_y + y_value][self.pos_x + x_value][0] not in id_opaque_blocks and \
                map_matrix[self.pos_y + y_value][self.pos_x + x_value][1] not in id_opaque_blocks:
            self.x_value = x_value
            self.y_value = y_value
            self.movement_pos_x, self.movement_pos_y = self.pos_x, self.pos_y
            return True
        if self.x_value == x_value and self.y_value == y_value:
            self.image = player_images["player"]
        return False

    def move(self):
        if self.x_value is not None and self.y_value is not None and \
                (abs((self.x_value * self.speed) / player_change_delay),
                 abs((self.y_value * self.speed) / player_change_delay)) < (abs(self.x_value), abs(self.y_value)):
            self.movement_pos_x = self.movement_pos_x + (self.x_value * self.speed) / player_change_delay
            self.movement_pos_y = self.movement_pos_y + (self.y_value * self.speed) / player_change_delay
            if self.counter < player_change_delay:
                self.rect = self.image.get_rect().move(tile_size * self.movement_pos_x, tile_size * self.movement_pos_y)
                if self.speed == 1.5:
                    self.counter += 2
                else:
                    self.counter += 1
                return True
            self.pos_x += self.x_value
            self.pos_y += self.y_value
            self.rect = self.image.get_rect().move(tile_size * self.pos_x, tile_size * self.pos_y)
            self.counter = 0
            return False

    def shoot(self, x_value, y_value):
        self.shot_pos_x, self.shot_pos_y = x_value, y_value
        if bullet_group.effects["fire_ball"]:
            self.player_channel.play(pygame.mixer.Sound(sounds["fire_ball"]), 0)
        else:
            self.player_channel.play(pygame.mixer.Sound(sounds["revolver_shot"]), 0)

        pygame.time.set_timer(PLAYERSHOTEVENT, 70)
        if self.effects["multi_shot"] != 0:
            for x, y in self.shot_pos.keys():
                Bullet(self.pos_x, self.pos_y, x, y, self.shot_pos[x, y])
        elif self.effects["triple_shot"] != 0:
            start_direction, end_direction = None, None
            if x_value == 1:
                start_direction, end_direction = 7, 10
            elif x_value == -1:
                start_direction, end_direction = 3, 6
            elif y_value == 1:
                start_direction, end_direction = 5, 8
            elif y_value == -1:
                start_direction, end_direction = 1, 4
            shot_pos_keys = list(self.shot_pos.keys())
            for ind in range(start_direction, end_direction):
                x, y = shot_pos_keys[ind % 8]
                Bullet(self.pos_x, self.pos_y, x, y, self.shot_pos[x, y])
        else:
            Bullet(self.pos_x, self.pos_y, x_value, y_value, self.shot_pos[x_value, y_value])

    #  Анимация движения
    def move_anim(self, is_moving):
        if is_moving:
            if self.x_value == -1:
                self.image = pygame.transform.flip(
                    anim_player_movement[(self.counter // len(anim_player_movement)) % len(anim_player_movement)],
                    True, False)
            else:
                self.image = anim_player_movement[
                    (self.counter // len(anim_player_movement)) % len(anim_player_movement)]
        else:
            self.image = player_images["player"]

    #  Анимация движения игрока, при стрельбе
    def shot_anim(self, counter):
        if counter != len(anim_player_shot):
            if self.shot_pos_x == -1:
                self.image = pygame.transform.flip(anim_player_shot[counter], True, False)
            else:
                self.image = anim_player_shot[counter]
            return True
        self.image = player_images["player"]
        return False

    def get_pos(self):
        return self.pos_x, self.pos_y

    def check_for_existence(self):
        if self.lives == 0:
            total_channel.stop()
            win_game_over_window("game_over")


#  Класс пули, образующегося при стрельбе "Player"
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, xn, yn, angle):
        super().__init__(bullet_group)
        self.x, self.y = x, y
        self.angle = angle
        self.xn, self.yn = xn, yn
        self.set_image()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(tile_size * self.x, tile_size * self.y)

    def set_image(self):
        if bullet_group.effects["fire_ball"]:
            self.image = pygame.transform.rotate(bullet_images["fire_ball"], self.angle)
        else:
            self.image = pygame.transform.rotate(bullet_images["bullet"], self.angle)

    def update(self):
        self.x += self.xn
        self.y += self.yn
        if 0 <= self.x < level_width and 0 <= self.y < level_height:
            if bullet_group.effects["fire_ball"] != 0:
                self.rect = self.image.get_rect().move(tile_size * self.x, tile_size * self.y)
            elif map_matrix[self.y][self.x][0] not in id_opaque_blocks and \
                    map_matrix[self.y][self.x][1] not in id_opaque_blocks:
                self.rect = self.image.get_rect().move(tile_size * self.x, tile_size * self.y)
            else:
                self.kill()
        else:
            self.kill()

    def removed(self):
        self.kill()


#  Редактирование групп. В некоторых хранится значения позиций и значения времени действия эффектов
class EnemyGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.effects = {"freezing": 0}
        self.enemy_pos = {}

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


class BoostGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.boost_pos = []

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


class DangerousTileGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.dangerous_tile_pos = []

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


class BulletGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.effects = {"fire_ball": 0}

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


#  Родительский класс врага
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(enemy_group)
        self.enemy_name = "zombie"
        self.sx, self.sy = x, y
        self.ex, self.ey = player.get_pos()
        self.enemy_channel = pygame.mixer.Channel(2)
        self.enemy_channel.set_volume(0.5)
        enemy_group.enemy_pos[self] = (self.sy, self.sx, self.enemy_name)
        self.the_way_pos = [(self.ex, self.ey)]
        self.enemy_matrix = [[0 for _ in range(level_width)] for _ in range(level_height)]
        self.enemy_matrix[self.sy][self.sx] = 1
        self.k = 0
        self.hit_cooldown = 2
        self.death_cooldown = 3
        self.counter = 0
        self.step = 1
        self.lives = 1
        self.action = "walking"
        self.x_value, self.y_value = None, None
        self.next_x, self.next_y = None, None
        self.movement_animation = [None]
        self.death_animation = [None]
        self.image = enemy_images[self.enemy_name]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(tile_size * x, tile_size * y)
        self.create_ways()

    def update(self):
        if self.dying_anim():
            return
        self.ex, self.ey = player.get_pos()
        self.the_way_pos = [(self.ex, self.ey)]
        self.enemy_matrix = [[0 for _ in range(level_width)] for _ in range(level_height)]
        self.move_anim()
        if self.counter == 0:
            self.enemy_matrix[int(self.sy)][int(self.sx)] = 1
            self.k = 0
            self.create_ways()
        if self.the_way_pos and self.counter == 0:
            self.next_x, self.next_y = self.the_way_pos.pop(-1)
            self.x_value, self.y_value = self.next_x - self.sx, self.next_y - self.sy
        if (self.next_x, self.next_y) != player.get_pos() and \
                (self.next_x, self.next_y) not in enemy_group.enemy_pos.values():
            self.sx = self.sx + self.x_value / 4
            self.sy = self.sy + self.y_value / 4
            enemy_group.enemy_pos[self] = (self.sy, self.sx, self.enemy_name)
            self.rect = self.image.get_rect().move(tile_size * self.sx, tile_size * self.sy)
        elif (self.next_x, self.next_y) == player.get_pos():
            self.image = enemy_images[self.enemy_name]
            if self.hit_cooldown == 0:
                self.enemy_channel.play(pygame.mixer.Sound(sounds["enemy_hit"]), 0)
                player.lives -= 1
                self.hit_cooldown = 3
                player.check_for_existence()
            else:
                self.hit_cooldown -= 1
        self.counter += 1

    #  Анимация движения
    def move_anim(self):
        if self.counter != 4:
            self.image = self.movement_animation[self.counter]
        else:
            self.counter = 0

    #  Анимация смерти
    def dying_anim(self):
        if self.action == "dying" and self.death_cooldown != -1 and self.lives == 0:
            self.image = self.death_animation[self.death_cooldown]
            self.death_cooldown -= 1
            return True
        elif self.death_cooldown == -1 and self.lives == 0:
            self.killed()
            self.action = "walking"
            self.death_cooldown = 3
            return False

    #  Создание правильного пути с помощью поиска в ширину
    def make_a_step(self):
        for y in range(level_height):
            for x in range(level_width):
                if self.enemy_matrix[y][x] == self.k:
                    if (y - 1) >= 0 and self.enemy_matrix[y - 1][x] == 0 and \
                            map_matrix[y - 1][x][0] not in id_opaque_blocks and \
                            map_matrix[y - 1][x][1] not in id_opaque_blocks:
                        self.enemy_matrix[y - 1][x] = self.k + 1
                    if (y + 1) < level_height and self.enemy_matrix[y + 1][x] == 0 and \
                            map_matrix[y + 1][x][0] not in id_opaque_blocks and \
                            map_matrix[y + 1][x][1] not in id_opaque_blocks:
                        self.enemy_matrix[y + 1][x] = self.k + 1
                    if (x - 1) >= 0 and self.enemy_matrix[y][x - 1] == 0 and \
                            map_matrix[y][x - 1][0] not in id_opaque_blocks and \
                            map_matrix[y][x - 1][1] not in id_opaque_blocks:
                        self.enemy_matrix[y][x - 1] = self.k + 1
                    if (x + 1) < level_width and self.enemy_matrix[y][x + 1] == 0 and \
                            map_matrix[y][x + 1][0] not in id_opaque_blocks and \
                            map_matrix[y][x + 1][1] not in id_opaque_blocks:
                        self.enemy_matrix[y][x + 1] = self.k + 1

    def create_ways(self):
        while self.enemy_matrix[self.ey][self.ex] == 0:
            self.k += 1
            self.make_a_step()
        self.find_current_way()

    def find_current_way(self):
        x, y = self.ex, self.ey
        self.k = self.enemy_matrix[self.ey][self.ex]
        while self.k > 1:
            if y > 0 and self.enemy_matrix[y - 1][x] == self.k - 1:
                x, y = x, y - 1
                self.the_way_pos.append((x, y))
                self.k -= 1
            elif y < level_height - 1 and self.enemy_matrix[y + 1][x] == self.k - 1:
                x, y = x, y + 1
                self.the_way_pos.append((x, y))
                self.k -= 1
            elif x > 0 and self.enemy_matrix[y][x - 1] == self.k - 1:
                x, y = x - 1, y
                self.the_way_pos.append((x, y))
                self.k -= 1
            elif x < level_width - 1 and self.enemy_matrix[y][x + 1] == self.k - 1:
                x, y = x + 1, y
                self.the_way_pos.append((x, y))
                self.k -= 1
        if self.step % 2 != 0:
            self.the_way_pos = self.the_way_pos[:len(self.the_way_pos) - 1][::self.step]
        else:
            self.the_way_pos = [self.the_way_pos[0]] + self.the_way_pos[1:len(self.the_way_pos) - 1:self.step]

    #  Проверка на смерть
    def killed(self):
        global enemy_killing_points
        self.enemy_channel.play(pygame.mixer.Sound(sounds["killing_enemies"]), 0)
        del enemy_group.enemy_pos[self]
        enemy_killing_points += 1
        self.kill()


#  Босс "Minotaur" в 3-ем уровне
class Minotaur(Enemy):
    def __init__(self, x, y, lives=10):
        super().__init__(x, y)
        self.enemy_name = "minotaur"
        self.movement_animation = anim_minotaur_movement
        self.death_animation = anim_minotaur_death
        self.hit_animation = anim_minotaur_hit
        self.lives = lives

        self.hit_counter = 0
        self.hit_cooldown = 5

    def update(self):
        if self.dying_anim():
            return
        self.ex, self.ey = player.get_pos()
        self.the_way_pos = [(self.ex, self.ey)]
        self.enemy_matrix = [[0 for _ in range(level_width)] for _ in range(level_height)]
        self.move_anim()
        if self.counter == 0:
            self.enemy_matrix[int(self.sy)][int(self.sx)] = 1
            self.k = 0
            self.create_ways()
        if self.the_way_pos and self.counter == 0:
            self.next_x, self.next_y = self.the_way_pos.pop(-1)
            self.x_value, self.y_value = self.next_x - self.sx, self.next_y - self.sy
        if (self.next_x, self.next_y) != player.get_pos() \
                and all([(self.next_x, self.next_y, name) not in enemy_group.enemy_pos.values()
                         for name in enemy_names]):
            self.sx = self.sx + self.x_value / 4
            self.sy = self.sy + self.y_value / 4
            enemy_group.enemy_pos[self] = (self.sy, self.sx, self.enemy_name)
            self.rect = self.image.get_rect().move(tile_size * self.sx, tile_size * self.sy)
        elif (self.next_x, self.next_y) == player.get_pos():
            self.image = enemy_images[self.enemy_name]
            if self.hit_cooldown == 0:
                self.enemy_channel.play(pygame.mixer.Sound(sounds["enemy_hit"]), 0)
                player.lives -= 1
                self.hit_cooldown = 5
                player.check_for_existence()
            else:
                self.hit_anim()
                self.hit_cooldown -= 1
        self.counter += 1

    # Проверка на смерть. Возвращение победы или поражения
    def is_killed(self):
        if self.lives == 0:
            return True
        return False

    def make_a_step(self):
        for y in range(level_height):
            for x in range(level_width):
                if self.enemy_matrix[y][x] == self.k:
                    if (y - 1) >= 0 and self.enemy_matrix[y - 1][x] == 0:
                        self.enemy_matrix[y - 1][x] = self.k + 1
                    if (y + 1) < level_height and self.enemy_matrix[y + 1][x] == 0:
                        self.enemy_matrix[y + 1][x] = self.k + 1
                    if (x - 1) >= 0 and self.enemy_matrix[y][x - 1] == 0:
                        self.enemy_matrix[y][x - 1] = self.k + 1
                    if (x + 1) < level_width and self.enemy_matrix[y][x + 1] == 0:
                        self.enemy_matrix[y][x + 1] = self.k + 1

    #  Анимация движения
    def move_anim(self):
        if self.counter != 4:
            self.image = self.movement_animation[self.counter % 3]
        else:
            self.counter = 0

    #  Анимация удара
    def hit_anim(self):
        if self.counter == 4:
            self.counter = 0
        if self.hit_counter != 5:
            self.image = self.hit_animation[self.hit_counter]
        else:
            self.hit_counter = 0

        self.hit_counter += 1

    #  Анимация смерти
    def dying_anim(self):
        if self.action == "dying" and self.death_cooldown != -1 and self.lives == 0:
            self.image = self.death_animation[-self.death_cooldown]
            self.death_cooldown -= 1
            return True
        elif self.death_cooldown == -1 and self.lives == 0:
            self.killed()
            self.action = "walking"
            return False


#  Класс простого зомби
class Zombie(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.enemy_name = "zombie"
        self.movement_animation = anim_zombie_movement
        self.death_animation = anim_zombie_death


#  Класс зомби, образующий "ToxicSlime" после хождения
class SickZombie(Zombie):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.enemy_name = "sick_zombie"
        self.movement_animation = anim_sick_zombie_movement
        self.death_animation = anim_sick_zombie_death
        self.hit_cooldown = 3

    def update(self):
        if self.action == "dying" and self.death_cooldown != -1:
            self.dying_anim()
            self.death_cooldown -= 1
            return
        elif self.death_cooldown == -1:
            self.killed()
            self.action = "walking"
            self.death_cooldown = 3
            return

        self.ex, self.ey = player.get_pos()
        self.the_way_pos = [(self.ex, self.ey)]
        self.enemy_matrix = [[0 for _ in range(level_width)] for _ in range(level_height)]
        self.move_anim()
        if self.counter == 0:
            self.enemy_matrix[int(self.sy)][int(self.sx)] = 1
            #  Образование "ToxicSlime"
            if (int(self.sx), int(self.sy)) not in dangerous_tile_group.dangerous_tile_pos:
                ToxicSlime(int(self.sx), int(self.sy))
            self.k = 0
            self.create_ways()
        if self.the_way_pos and self.counter == 0:
            self.next_x, self.next_y = self.the_way_pos.pop(-1)
            self.x_value, self.y_value = self.next_x - self.sx, self.next_y - self.sy
        if (self.next_x, self.next_y) != player.get_pos() and \
                all([(self.next_x, self.next_y, name) not in enemy_group.enemy_pos.values() for name in enemy_names]):
            self.sx = self.sx + self.x_value / 4
            self.sy = self.sy + self.y_value / 4
            enemy_group.enemy_pos[self] = (self.sy, self.sx, self.enemy_name)
            self.rect = self.image.get_rect().move(tile_size * self.sx, tile_size * self.sy)
        elif (self.next_x, self.next_y) == player.get_pos():
            self.image = enemy_images[self.enemy_name]
            if self.hit_cooldown == 0:
                self.enemy_channel.play(pygame.mixer.Sound(sounds["enemy_hit"]), 0)
                player.lives -= 1
                self.hit_cooldown = 3
                player.check_for_existence()
            else:
                self.hit_cooldown -= 1
        self.counter += 1


#  Класс быстрых зомби
class FastZombie(Zombie):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.enemy_name = "fast_zombie"
        self.movement_animation = anim_fast_zombie_movement
        self.death_animation = anim_fast_zombie_death
        self.step = 2


#  Класс слизи, образующейся после хождения "SickZombie"
class ToxicSlime(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(dangerous_tile_group)
        self.line_length = 10 * 4
        dangerous_tile_group.dangerous_tile_pos.append((x, y))
        self.slime_channel = pygame.mixer.Channel(4)
        self.slime_channel.set_volume(0.5)
        self.image = special_images["slime"]
        self.hit_cooldown = 10
        self.rect = self.image.get_rect().move(tile_size * x, tile_size * y)

    def update(self):
        if pygame.sprite.spritecollideany(self, player_group):
            if self.hit_cooldown == 0:
                self.slime_channel.play(pygame.mixer.Sound(sounds["burning_slime"]), 0)
                self.hit_cooldown = 10
                player.lives -= 1
                player.check_for_existence()
            else:
                self.hit_cooldown -= 1
        if self.line_length == 0:
            self.kill()
        self.line_length -= 1


#  Класс бустов, выпадающих с неба
class Boosts(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, boost_name):
        super().__init__(boost_group)
        self.pos_x = pos_x
        self.pos_y = pos_y
        boost_group.boost_pos.append((self.pos_x, self.pos_y, boost_name))
        self.start_y = self.pos_y - (self.pos_y - 10 if self.pos_y - 10 > 0 else self.pos_y)
        self.boost_name = boost_name
        self.boost_channel = pygame.mixer.Channel(3)
        self.boost_channel.set_volume(0.5)
        self.width, self.height = boost_images[self.boost_name].get_size()
        self.par_width, self.par_height = special_images["parachute"].get_size()
        self.image = pygame.Surface([self.width, self.height + self.par_height - self.height // 1.5], pygame.SRCALPHA)
        self.image.blit(boost_images[boost_name], (0, self.par_height - self.height // 1.5))
        self.image.blit(special_images["parachute"], (0, 0))
        self.rect = self.image.get_rect().move(tile_size * self.pos_x, tile_size * self.start_y)
        self.mask = None

    def distribution_of_boosts(self):
        self.boost_channel.play(pygame.mixer.Sound(sounds["use_boost"]), 0)
        if self.boost_name == "apple":
            player.lives = player.lives + 1 if player.lives + 1 <= 4 else player.lives
        elif self.boost_name == "fire_ball":
            bullet_group.effects[self.boost_name] = 10
        elif self.boost_name == "triple_shot":
            player.effects[self.boost_name] = 10
        elif self.boost_name == "multi_shot":
            player.effects[self.boost_name] = 10
        elif self.boost_name == "speed_increase":
            player.effects[self.boost_name] = 10
        elif self.boost_name == "freezing":
            enemy_group.effects[self.boost_name] = 10

    def update(self):
        if self.start_y < self.pos_y:
            self.rect = self.image.get_rect().move(tile_size * self.pos_x, tile_size * self.start_y)
            self.start_y += 1 / boost_change_delay
        else:
            self.image = boost_images[self.boost_name]
            self.rect = self.image.get_rect().move(tile_size * self.pos_x, tile_size * self.pos_y)
            self.mask = pygame.mask.from_surface(self.image)
            if pygame.sprite.collide_mask(self, player):
                self.distribution_of_boosts()
                self.kill()


#  Класс камеры
class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        screen.blit(obj.image, (obj.rect.x + self.dx, obj.rect.y + self.dy))

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = - (target.rect.y + target.rect.h // 2 - HEIGHT // 2)


#  Класс тайлов
class Tile(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__(all_sprites)
        self.image = image
        self.rect = self.image.get_rect().move(pos)


#  Функция, которая проверяет правильность пути и возвращает изображение
def load_image(path, filename):
    rel_path = os.path.join(*path, filename)
    if not os.path.isfile(rel_path):
        print(f"Изображения в пути {rel_path} не существует")
        sys.exit()
    image = pygame.image.load(rel_path)
    return image


#  Функция, которая проверяет правильность пути и возвращает уже соединенный путь
def give_path(path, filename):
    rel_path = os.path.join(*path, filename)
    if not os.path.isfile(rel_path):
        print(f"Файла в пути {rel_path} не существует")
        sys.exit()
    return rel_path


#  Принудительный выход
def terminate():
    pygame.quit()
    sys.exit()


#  Очищение всех групп при выборе сохранения или загрузке нового уровня
def cleaning_groups():
    global all_sprites, player_group, enemy_group, boost_group, map, map_matrix, player, dangerous_tile_group, \
        bullet_group
    player = None
    all_sprites.empty()
    all_sprites = pygame.sprite.Group()
    dangerous_tile_group = DangerousTileGroup()
    enemy_group = EnemyGroup()
    player_group = pygame.sprite.Group()
    boost_group = BoostGroup()
    enemy_group = EnemyGroup()
    bullet_group = BulletGroup()
    map = pytmx.load_pygame(levels[f"level_{level_value}"])
    map_matrix = [[(map.tiledgidmap[map.get_tile_gid(i, j, 0)],
                    map.tiledgidmap[map.get_tile_gid(i, j, 1)]
                    if map.get_tile_gid(i, j, 1) != 0 else None)
                   for i in range(level_width)] for j in range(level_height)]
    generate_map()
    pygame.time.set_timer(DROPBOOSTEVENT, int(6000 * difficulty))
    pygame.time.set_timer(ENEMYSPAWNEVENT, int(5000 * (2 - difficulty)))
    pygame.time.set_timer(BULLETFLIGHTEVENT, 100)
    pygame.time.set_timer(ENEMYMOVEVENT, 150)
    pygame.time.set_timer(BOOSTFLIGHTEVENT, 20)
    pygame.time.set_timer(TILEUPDATINGEVENT, 500)
    pygame.time.set_timer(BOOSTTIMECHANGEEVENT, 1000)
    pygame.time.set_timer(HEARTVALUESHOWEVENT, 300)


#  Создание карты
def generate_map():
    for y in range(level_height):
        for x in range(level_width):
            down_image = map.get_tile_image(x, y, 0)
            roof_image = map.get_tile_image(x, y, 1)
            Tile(down_image, (tile_size * x, tile_size * y))
            if roof_image is not None:
                Tile(roof_image, (tile_size * x, tile_size * y))


#  Создание второстепенных окошек в игре - показ хп, очков убитых монстров
def draw_secondary_windows(heard_value_counter, lives):
    pygame.draw.rect(screen, pygame.color.Color((29, 30, 51)), ((WIDTH - 240, 0), (240, 64)))

    rect_width, rect_height = 150, 50
    pygame.draw.rect(screen, pygame.color.Color((29, 30, 51)),
                     ((WIDTH - rect_width, HEIGHT - rect_height), (rect_width, rect_height)))
    font = pygame.font.Font(None, 25)
    text_zombie_point = font.render(f"Zombie points: {enemy_killing_points}", True, (255, 255, 255))
    text_width, text_height = text_zombie_point.get_size()
    screen.blit(text_zombie_point, (WIDTH - rect_width + (rect_width - text_width) // 2,
                                    HEIGHT - rect_height + (rect_height - text_height) // 2))
    if lives == 4:
        screen.blit(pygame.transform.scale(load_image(["data", "images", "life", "fulllife"],
                                                      f"h{heard_value_counter}.png"), (240, 64)), (WIDTH - 240, 0))
    if lives == 3:
        screen.blit(pygame.transform.scale(load_image(["data", "images", "life", "almosthalflife"],
                                                      f"h{heard_value_counter}.png"), (240, 64)), (WIDTH - 240, 0))
    if lives == 2:
        screen.blit(pygame.transform.scale(load_image(["data", "images", "life", "halflife"],
                                                      f"h{heard_value_counter}.png"), (240, 64)), (WIDTH - 240, 0))
    if lives == 1:
        screen.blit(pygame.transform.scale(load_image(["data", "images", "life", "onelife"],
                                                      f"h{heard_value_counter}.png"), (240, 64)), (WIDTH - 240, 0))
    if lives == 0:
        screen.blit(pygame.transform.scale(load_image(["data", "images", "life", "death"],
                                                      f"h{heard_value_counter % 3}.png"), (240, 64)), (WIDTH - 240, 0))

    if minotaur is not None:
        font = pygame.font.Font(None, 50)
        rect_width, rect_height = 300, 64
        pygame.draw.rect(screen, pygame.color.Color((139, 69, 19)), ((0, 0), (rect_width, rect_height)))
        text_minotaur_health = font.render(f"Boss health: {minotaur.lives}", True, (255, 255, 255))
        text_width, text_height = text_minotaur_health.get_size()
        screen.blit(text_minotaur_health, (0, (rect_height - text_height) // 2))
        screen.blit(special_images["heart"], (rect_width - (rect_width - text_width), (rect_height - text_height) // 2))


#  Окно, показываюшаяся после выигрыша или проигрыша
def win_game_over_window(end):
    global level_value, minotaur, player, player_group, enemy_killing_points
    pygame.display.set_caption("King of Empires")
    total_channel.stop()
    if end == "win":
        pygame.mixer.music.load(sounds["win"])
    else:
        pygame.mixer.music.load(sounds["game_over"])
    pygame.mixer.music.play(0)
    manager = pygame_gui.UIManager((WIDTH, HEIGHT))
    to_the_main_menu_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 150, HEIGHT // 2), (300, 100)),
        text="",
        manager=manager)
    clock = pygame.time.Clock()
    i = 0
    while True:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == to_the_main_menu_button:
                    minotaur = None
                    level_value = 1
                    enemy_killing_points = 0
                    cleaning_groups()
                    player = Player(pl_x, pl_y)
                    player.image = player_images["player"]
                    return main_menu("in_init")
            manager.process_events(event)

        if i != 101:
            if end == "win":
                bg = special_images["win_background"].convert(screen)
            else:
                bg = special_images["game_over_background"]
            bg.set_colorkey((255, 0, 255))
            bg.set_alpha(i)
            screen.blit(bg, (0, 0))
            i += 1
        manager.update(time_delta)
        to_the_main_menu_button.set_image(win_game_over_button_images["to_the_main_menu_button"])
        manager.draw_ui(screen)
        pygame.display.update()


#  Главное окно. Появляется при запуске программы
def main_menu(place_of_execution):
    pygame.display.set_caption("King of Empires")
    pygame.mixer.music.load(sounds["main_window_music"])
    pygame.mixer.music.play(-1)
    manager = pygame_gui.UIManager((WIDTH, HEIGHT))
    play_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 150, WIDTH // 2 + 30), (300, 100)),
        text="",
        manager=manager
    )
    load_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 150, HEIGHT // 2 + 150), (300, 100)),
        text="",
        manager=manager)
    settings_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 150, HEIGHT // 2 + 270), (300, 100)),
        text="",
        manager=manager)

    BACKGROUNDCHANGEEVENT = pygame.USEREVENT + 100
    pygame.time.set_timer(BACKGROUNDCHANGEEVENT, 60)
    cap = cv2.VideoCapture(give_path(["data", "animations"], "fire.mov"))
    succsess, image = cap.read()
    shape = image.shape[1::-1]
    clock = pygame.time.Clock()
    while True:
        time_delta = clock.tick(60) / 1000.0
        success, image = cap.read()
        if image is None:
            cap = cv2.VideoCapture(give_path(["data", "animations"], "fire.mov"))
            success, image = cap.read()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                pygame.mixer.music.stop()
                if event.ui_element == play_button:
                    pygame.time.set_timer(BACKGROUNDCHANGEEVENT, 0)
                    total_channel.play(pygame.mixer.Sound(sounds["game_music"]), -1)
                    total_channel.set_volume(0.2)
                    return
                if event.ui_element == settings_button:
                    if place_of_execution == "in_init":
                        settings()
                    elif place_of_execution == "in_game":
                        clicked = save_load_game_window("save")
                        if clicked:
                            return
                    pygame.mixer.music.play(-1)
                if event.ui_element == load_button:
                    clicked = save_load_game_window("load")
                    if clicked:
                        return
                    pygame.mixer.music.play(-1)
            if event.type == BACKGROUNDCHANGEEVENT:
                bg = pygame.transform.scale(pygame.image.frombuffer(image.tobytes(), shape, "BGR"),
                                            (800, 800)).convert(screen)
                bg.set_colorkey((255, 0, 255))
                bg.set_alpha(50)
                screen.blit(load_image(["data", "images"], f"background.png"), (0, 0))
                manager.update(time_delta)
                if place_of_execution == "in_init":
                    play_button.set_image(main_menu_button_images["play_button"])
                    settings_button.set_image(main_menu_button_images["settings_button"])
                if place_of_execution == "in_game":
                    play_button.set_image(main_menu_button_images["continue_button"])
                    settings_button.set_image(main_menu_button_images["save_button"])
                load_button.set_image(main_menu_button_images["load_button"])
                manager.draw_ui(screen)
                screen.blit(bg, (0, 0))
            pygame.display.set_caption("King of Empires")
            manager.process_events(event)
        pygame.display.update()


#  Окно настроек в главном окне
def settings():
    global difficulty
    pygame.display.set_caption("Settings")
    manager = pygame_gui.UIManager((WIDTH, HEIGHT))
    easy_difficulty_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50, HEIGHT // 2), (200, 200)),
                                                          manager=manager,
                                                          text="")
    medium_difficulty_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, HEIGHT // 2), (200, 200)),
                                                            manager=manager,
                                                            text="")
    hard_difficulty_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((550, HEIGHT // 2), (200, 200)),
                                                          manager=manager,
                                                          text="")
    clock = pygame.time.Clock()
    while True:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == hard_difficulty_button:
                    difficulty = 1.6
                if event.ui_element == medium_difficulty_button:
                    difficulty = 1.2
                if event.ui_element == easy_difficulty_button:
                    difficulty = 1
                return True
            hard_difficulty_button.set_image(settings_button_images["hard_button"])
            medium_difficulty_button.set_image(settings_button_images["medium_button"])
            easy_difficulty_button.set_image(settings_button_images["easy_button"])
            screen.blit(special_images["settings_background"], (0, 0))
            manager.draw_ui(screen)
            manager.process_events(event)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            return False
        manager.update(time_delta)
        pygame.display.update()


#  Окно сохранения и загрузки в главном окне
def save_load_game_window(mode):
    global level_value, player_group, difficulty, player, minotaur, enemy_killing_points, enemy_group, boost_group
    manager = pygame_gui.UIManager((WIDTH, HEIGHT))
    saves = [pygame_gui.elements.UIButton(relative_rect=pygame.Rect(((x + 1) * 40 + x * 112, HEIGHT // 2), (112, 112)),
                                          manager=manager, text="") for x in range(5)]
    clock = pygame.time.Clock()
    while True:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                con = sqlite3.connect(give_path(["databases"], "database_of_saves.db"))
                cur = con.cursor()
                conservation_ind = saves.index(event.ui_element)
                if mode == "load":
                    fullness = cur.execute(
                        f"""SELECT saves.level_value FROM saves WHERE saves.ID = {conservation_ind}""").fetchall()[0][0]
                    if fullness != "None":
                        total_channel.play(pygame.mixer.Sound(sounds["game_music"]), -1)
                        total_channel.set_volume(0.2)
                        id, level_value, enemy_killing_points, difficulty, p_values, z_values, b_values = \
                            [x for x in cur.execute(
                                f"""SELECT * FROM saves WHERE saves.ID = {conservation_ind}""")][0]
                        minotaur = None
                        cleaning_groups()
                        player = Player(*pickle.loads(p_values))
                        if z_values:
                            for sx, sy, enemy_name in pickle.loads(z_values):
                                if enemy_name == "zombie":
                                    enemy_group.add(Zombie(sx, sy))
                                elif enemy_name == "sick_zombie":
                                    enemy_group.add(SickZombie(sx, sy))
                                elif enemy_name == "fast_zombie":
                                    enemy_group.add(FastZombie(sx, sy))
                                elif enemy_name == "minotaur":
                                    minotaur = Minotaur(sx, sy)
                        if b_values:
                            for value in pickle.loads(b_values):
                                boost_group.add(Boosts(*value))
                        return True
                elif mode == "save":
                    p_sprite_values = sqlite3.Binary(pickle.dumps(
                        (player_group.sprites()[0].pos_x, player_group.sprites()[0].pos_y),
                        pickle.HIGHEST_PROTOCOL))
                    z_sprite_values = sqlite3.Binary(pickle.dumps(
                        [(int(value[0]), int(value[1]), value[2]) for value in enemy_group.enemy_pos.values()],
                        pickle.HIGHEST_PROTOCOL))
                    b_sprite_values = sqlite3.Binary(pickle.dumps(
                        [(value[0], value[1], value[2]) for value in boost_group.boost_pos],
                        pickle.HIGHEST_PROTOCOL))
                    cur.execute(f"""REPLACE INTO saves(ID, level_value, enemy_killing_points, difficulty, 
                    player_group, zombie_group, boost_group) 
                    VALUES({conservation_ind}, {level_value}, {enemy_killing_points}, {difficulty}, ?, ?, ?) """,
                                (p_sprite_values, z_sprite_values, b_sprite_values))
                    con.commit()
                    return True
            screen.blit(special_images["save_background"], (0, 0))
            [saves[i].set_image(save_button_images[f"save_button{i}"]) for i in range(len(saves))]
            manager.draw_ui(screen)
            manager.process_events(event)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            return False
        manager.update(time_delta)
        pygame.display.update()


# Здесь происходит вырезание одной общей картинки тайлов на отдельные части
def cut_sheet(desired_path, columns, rows):
    sheet = load_image(*desired_path)
    frames = []
    sheet_width, sheet_height = sheet.get_size()
    frame_width, frame_height = sheet_width // rows, sheet_height // columns
    for j in range(columns):
        for i in range(rows):
            frames.append(sheet.subsurface((frame_width * i, frame_height * j), (frame_width, frame_height)))
    return frames


#  Инициализация и создание всех переменных
pygame.init()
enemy_pos = {"level_1": [(1, 1), (1, 38), (38, 38), (38, 1)], "level_2": [(1, 39), (32, 10), (35, 10), (35, 15)],
             "level_3": [(1, 1), (1, 38), (38, 38), (38, 1)]}
difficulty = 1
id_opaque_blocks = [2054, 2310, 2118, 2055, 2310, 2118, 522, 521, 513, 514, 528, 527, 519, 520, 550, 572, 552, 551,
                    515, 516, 524, 523, 2120, 2056, 2309, 3719, 2184, 2245, 2246, 2182, 2183, 717, 721, 715, 724, 722,
                    713, 723, 4773, 4868, 4860, 4728, 4727, 4719, 4720, 4776, 4768, 4985, 4970, 4971, 4987,
                    4986, 4985, 4770, 4772, 4899, 4902, 4897, 4908, 4752, 4751, 1512, 4452, 1574, 1638, 4452,
                    1638, 1637, 1576, 4846, 4824, 4823, 4815, 4816, 4866, 4869, 5733, 5725, 4870, 5009, 5011,
                    5017, 5012, 5020, 5019, 4872, 4864, 5740, 5748, 5749, 5741, 5709, 5717, 4848, 4847, 5003, 4994,
                    5004, 5002, 4995, 4996, 5001, 716, 1448, 1510, 4969]
id_forbidden_blocks = [9371, 9250, 9190, 1511, 9189]
SIZE = WIDTH, HEIGHT = 800, 800
enemy_names = ["zombie", "sick_zombie", "fast_zombie", "minotaur"]
boost_names = ["apple", "triple_shot", "fire_ball", "multi_shot", "speed_increase", "freezing"]
MOVEMENTPLAYEREVENT = pygame.USEREVENT + 10
PLAYERSHOTEVENT = pygame.USEREVENT + 11
MOVEMENTBULLETEVENT = pygame.USEREVENT + 20
ENEMYSPAWNEVENT = pygame.USEREVENT + 30
ENEMYMOVEVENT = pygame.USEREVENT + 31
FASTZOMBIEMOVEEVENT = pygame.USEREVENT + 32
DROPBOOSTEVENT = pygame.USEREVENT + 40
BOOSTFLIGHTEVENT = pygame.USEREVENT + 41
BOOSTTIMECHANGEEVENT = pygame.USEREVENT + 42
BULLETFLIGHTEVENT = pygame.USEREVENT + 50
TILEUPDATINGEVENT = pygame.USEREVENT + 60
HEARTVALUESHOWEVENT = pygame.USEREVENT + 70
screen = pygame.display.set_mode(SIZE)

player_images = {"player": load_image(["data", "images"], "archaeologist.png")}
enemy_images = {"zombie": load_image(["data", "images"], "zombie.png"),
                "sick_zombie": load_image(["data", "images"], "sick_zombie.png"),
                "fast_zombie": load_image(["data", "images"], "fast_zombie.png"),
                "minotaur": load_image(["data", "images"], "minotaur.png")}
bullet_images = {"bullet": load_image(["data", "images"], "bullet.png"),
                 "fire_ball": load_image(["data", "images"], "fire_bullet.png")}
boost_images = {"apple": load_image(["data", "images"], "apple.png"),
                "triple_shot": load_image(["data", "images"], "triple_shot.png"),
                "fire_ball": load_image(["data", "images"], "fire_ball.png"),
                "multi_shot": load_image(["data", "images"], "multi_shot.png"),
                "speed_increase": load_image(["data", "images"], "speed_increase.png"),
                "freezing": load_image(["data", "images"], "freezing.png")}

main_menu_button_images = {"play_button": load_image(["data", "images", "main_menu_buttons"], "play_button.png"),
                           "load_button": load_image(["data", "images", "main_menu_buttons"], "load_button.png"),
                           "settings_button": load_image(["data", "images", "main_menu_buttons"], "settings_button.png"),
                           "continue_button": load_image(["data", "images", "main_menu_buttons"], "continue_button.png"),
                           "save_button": load_image(["data", "images", "main_menu_buttons"], "save_button.png")}
save_button_images = dict((f"save_button{i}", load_image(["data", "images", "save_buttons"], f"save_button{i}.png"))
                          for i in range(5))
settings_button_images = {"hard_button": load_image(["data", "images", "settings_buttons"], "hard_button.png"),
                          "medium_button": load_image(["data", "images", "settings_buttons"], "medium_button.png"),
                          "easy_button": load_image(["data", "images", "settings_buttons"], "easy_button.png")}
win_game_over_button_images = {
    "to_the_main_menu_button": load_image(["data", "images", "win_game_over_buttons"], "to_the_main_menu_button.png")
}

anim_player_movement = cut_sheet([["data", "animations", "player"], "movement.png"], 1, 4)
anim_player_shot = cut_sheet([["data", "animations", "player"], "shot.png"], 1, 4)

anim_zombie_movement = cut_sheet([["data", "animations", "zombie"], "movement.png"], 1, 4)
anim_zombie_death = cut_sheet([["data", "animations", "zombie"], "death.png"], 1, 4)

anim_sick_zombie_movement = cut_sheet([["data", "animations", "sick_zombie"], "movement.png"], 1, 4)
anim_sick_zombie_death = cut_sheet([["data", "animations", "sick_zombie"], "death.png"], 1, 4)

anim_fast_zombie_movement = cut_sheet([["data", "animations", "fast_zombie"], "movement.png"], 1, 4)
anim_fast_zombie_death = cut_sheet([["data", "animations", "fast_zombie"], "death.png"], 1, 4)

anim_minotaur_movement = cut_sheet([["data", "animations", "minotaur"], "movement.png"], 1, 3)
anim_minotaur_hit = cut_sheet([["data", "animations", "minotaur"], "hit.png"], 1, 5)
anim_minotaur_death = cut_sheet([["data", "animations", "minotaur"], "death.png"], 1, 4)

special_images = {"parachute": load_image(["data", "images"], "parachute.png"),
                  "slime": load_image(["data", "images"], "slime.png"),
                  "settings_background": load_image(["data", "images"], "settings_background.png"),
                  "save_background": load_image(["data", "images"], "save_background.png"),
                  "win_background": load_image(["data", "images"], "win_background.png"),
                  "game_over_background": load_image(["data", "images"], "game_over_background.png"),
                  "heart": load_image(["data", "images"], "heart.png")}

sounds = {"game_music": give_path(["data", "soundtracks"], "Vibe Mountain - Operatic 3.mp3"),
          "main_window_music": give_path(["data", "soundtracks"], "Steam Powered Flying Machine.mp3"),
          "revolver_shot": give_path(["data", "soundtracks"], "revolver_shot.mp3"),
          "fire_ball": give_path(["data", "soundtracks"], "fire_ball.mp3"),
          "enemy_hit": give_path(["data", "soundtracks"], "enemy_hit.mp3"),
          "use_boost": give_path(["data", "soundtracks"], "use_boost.mp3"),
          "killing_enemies": give_path(["data", "soundtracks"], "killing_enemies.mp3"),
          "burning_slime": give_path(["data", "soundtracks"], "burning_slime.mp3"),
          "win": give_path(["data", "soundtracks"], "win.wav"),
          "game_over": give_path(["data", "soundtracks"], "game_over.mp3")}

levels = {"level_1": give_path(["data", "levels"], "level_1.tmx"),
          "level_2": give_path(["data", "levels"], "level_2.tmx"),
          "level_3": give_path(["data", "levels"], "level_3.tmx")}
level_value = 1
map = pytmx.load_pygame(levels[f"level_{level_value}"])
level_width = map.width
level_height = map.height
tile_size = map.tilewidth
map_matrix = [[(map.tiledgidmap[map.get_tile_gid(i, j, 0)],
                map.tiledgidmap[map.get_tile_gid(i, j, 1)]
                if map.get_tile_gid(i, j, 1) != 0 else None)
               for i in range(level_width)] for j in range(level_height)]

camera = Camera()
dangerous_tile_group = DangerousTileGroup()
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
boost_group = BoostGroup()
enemy_group = EnemyGroup()
bullet_group = BulletGroup()

total_channel = pygame.mixer.Channel(0)

pl_x, pl_y = 12, 12
boss_x, boss_y = 20, 20
enemy_killing_points = 0
player_change_delay = 16
boost_change_delay = 16
minotaur = None
player = Player(pl_x, pl_y)

generate_map()
main_menu("in_init")
pygame.time.set_timer(DROPBOOSTEVENT, int(6000 * difficulty))
pygame.time.set_timer(ENEMYSPAWNEVENT, int(5000 * (2 - difficulty)))
pygame.time.set_timer(BULLETFLIGHTEVENT, 100)
pygame.time.set_timer(ENEMYMOVEVENT, 150)
pygame.time.set_timer(BOOSTFLIGHTEVENT, 20)
pygame.time.set_timer(TILEUPDATINGEVENT, 500)
pygame.time.set_timer(BOOSTTIMECHANGEEVENT, 1000)
pygame.time.set_timer(HEARTVALUESHOWEVENT, 300)


#  Главный цикл игры
def main():
    global level_value, enemy_killing_points, minotaur, player, player_group
    running = True
    shot_cooldown = 0
    animation_counter = 0
    heart_show_counter = 1
    pygame.display.set_caption("King of Empires")
    while running:
        move_x, move_y = 0, 0

        screen.fill(pygame.color.Color((47, 47, 46)))
        camera.update(player)
        all_sprites.update()
        for bullet in bullet_group.sprites():
            intersection = False
            for enemy in enemy_group.sprites():
                if pygame.sprite.collide_mask(bullet, enemy):
                    enemy.action = "dying"
                    enemy.lives -= 1
                    intersection = True
            if intersection:
                bullet.removed()

        if enemy_killing_points >= 5 and (level_value + 1) <= 3:
            shot_cooldown = 0
            animation_counter = 0
            level_value += 1
            enemy_killing_points = 0
            cleaning_groups()
            player = Player(pl_x, pl_y)
        if level_value == 3 and minotaur is None:
            minotaur = Minotaur(boss_x, boss_y)
        if minotaur is not None and minotaur.is_killed():
            shot_cooldown = 0
            animation_counter = 0
            win_game_over_window("win")

        for sprite in all_sprites:
            camera.apply(sprite)
        for sprite in dangerous_tile_group:
            camera.apply(sprite)
        for sprite in player_group:
            camera.apply(sprite)
        for sprite in bullet_group:
            camera.apply(sprite)
        for sprite in boost_group:
            camera.apply(sprite)
        for sprite in enemy_group:
            camera.apply(sprite)
        draw_secondary_windows(heart_show_counter, player.lives)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == MOVEMENTPLAYEREVENT:
                outcome_movement = player.move()
                player.move_anim(True)
                if not outcome_movement and player.counter == 0:
                    pygame.time.set_timer(MOVEMENTPLAYEREVENT, 0)
                if player.counter:
                    pygame.time.set_timer(MOVEMENTPLAYEREVENT, player_change_delay)
            if event.type == PLAYERSHOTEVENT:
                outcome_shot = player.shot_anim(animation_counter)
                animation_counter = animation_counter + 1
                if not outcome_shot:
                    pygame.time.set_timer(PLAYERSHOTEVENT, 0)
                    animation_counter = 0
            if event.type == DROPBOOSTEVENT and len(boost_group) < 5:
                x, y = randint(0, level_width - 1), randint(0, level_height - 1)
                while map_matrix[y][x][0] in id_opaque_blocks or map_matrix[y][x][1] in id_opaque_blocks or \
                        map_matrix[y][x][0] in id_forbidden_blocks or map_matrix[y][x][1] in id_forbidden_blocks or \
                        any([(x, y, name) in boost_group.boost_pos for name in boost_names]):
                    x, y = randint(0, level_width - 1), randint(0, level_height - 1)
                new_boost_name = choice(list(boost_images.keys()))
                Boosts(x, y, new_boost_name)
            if event.type == BULLETFLIGHTEVENT:
                bullet_group.update()
            if event.type == BOOSTFLIGHTEVENT:
                boost_group.update()
            if event.type == ENEMYMOVEVENT and not enemy_group.effects["freezing"]:
                enemy_group.update()
                dangerous_tile_group.update()
            if event.type == ENEMYSPAWNEVENT and not enemy_group.effects["freezing"]:
                x, y = choice(enemy_pos[f"level_{level_value}"])
                while (x, y) in enemy_group.enemy_pos.keys():
                    x, y = choice(enemy_pos)
                chance = random()
                if level_value == 1:
                    if 0 <= chance <= 0.8:
                        Zombie(x, y)
                    if 0.8 < chance <= 1:
                        SickZombie(x, y)
                elif level_value == 2:
                    if 0 <= chance <= 0.3:
                        Zombie(x, y)
                    if 0.3 < chance <= 0.8:
                        SickZombie(x, y)
                    elif 0.8 < chance <= 1:
                        FastZombie(x, y)
                elif level_value == 3:
                    if 0 <= chance <= 0.1:
                        Zombie(x, y)
                    if 0.1 < chance <= 0.5:
                        SickZombie(x, y)
                    elif 0.5 < chance <= 1:
                        FastZombie(x, y)

            if event.type == BOOSTTIMECHANGEEVENT:
                values = list(player.effects.values())
                for i in range(len(values)):
                    values[i] = values[i] - 1 if values[i] - 1 > 0 else 0
                player.effects = dict(zip(list(player.effects.keys()), values))
                bullet_group.effects["fire_ball"] = bullet_group.effects["fire_ball"] - 1 if \
                    bullet_group.effects["fire_ball"] - 1 > 0 else 0
                enemy_group.effects["freezing"] = enemy_group.effects["freezing"] - 1 if \
                    enemy_group.effects["freezing"] - 1 > 0 else 0
            if event.type == HEARTVALUESHOWEVENT:
                heart_show_counter = (heart_show_counter + 1) % 14 + 1
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE] and not player.counter:
                total_channel.stop()
                main_menu("in_game")
                total_channel.play(pygame.mixer.Sound(sounds["game_music"]), -1)
            if keys[pygame.K_w] and not player.counter:
                move_y = -1
            if keys[pygame.K_s] and not player.counter:
                move_y = 1
            if keys[pygame.K_a] and not player.counter:
                move_x = -1
            if keys[pygame.K_d] and not player.counter:
                move_x = 1
            if not keys[pygame.K_w] and not keys[pygame.K_s] and not keys[pygame.K_a] and not keys[pygame.K_d] and \
                    not player.counter and not animation_counter:
                player.move_anim(False)
            if keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]:
                if player.check_move(move_x, move_y):
                    pygame.time.set_timer(MOVEMENTPLAYEREVENT, player_change_delay)
            if not shot_cooldown and not player.counter:
                if keys[pygame.K_UP] and (move_x == 0 and move_y == 0):
                    player.shoot(0, -1)
                    shot_cooldown = 100
                elif keys[pygame.K_DOWN] and (move_x == 0 and move_y == 0):
                    player.shoot(0, 1)
                    shot_cooldown = 100
                elif keys[pygame.K_LEFT] and (move_x == 0 and move_y == 0):
                    player.shoot(-1, 0)
                    shot_cooldown = 100
                elif keys[pygame.K_RIGHT] and (move_x == 0 and move_y == 0):
                    player.shoot(1, 0)
                    shot_cooldown = 100
            if shot_cooldown:
                shot_cooldown = shot_cooldown - 1 if shot_cooldown > 0 else 0
        pygame.display.flip()
    pygame.mixer.music.stop()
    pygame.quit()


# Запуск
if __name__ == "__main__":
    main()
