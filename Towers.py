import pygame
from math import sqrt, degrees, atan2, ceil
import Bullets
import UI
import Settings
from Icons import remove_folder, set_folder_icon
import os
from random import choice
from PIL import Image
from shutil import copy
import Money
import MathExtented
from re import search

towers = []
temp_icons = []


class AttackTower:
    COST = None

    def __init__(self, folder_path, name, building_name, image_path, pos, health, raw_pos):
        self.image_path = image_path

        self.building_name = building_name

        self.folder_path = folder_path
        self.name = name

        self.power = 10

        self.full_health = health
        self.health = health

        self.pos = pygame.Vector2(pos)
        self.raw_pos = pygame.Vector2(raw_pos)

        self.image = pygame.image.load(self.image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=self.pos)

        self.attack_rate = 2
        self.last_attack = 0

        self.health_bar = UI.Bar((self.pos[0] + Settings.ICON_WIDTH//2, self.pos[1] - Settings.ICON_HEIGHT//4),
                                 "GREEN", self.full_health, self.health, 0.5, group=towers, owner=self)
        UI.ui_elements.append(self.health_bar)

        self.attack_sound_effects = os.listdir("SoundEffects/Towers/Gunshots")
        self.attack_SFX = None

        self.death_sound_effects = os.listdir("SoundEffects/Towers/Death")
        self.death_SFX = None

        self.angle = 0

        self.is_rotated = False

        self.time_since_start = 0

        image = pygame.Surface((256, 256), pygame.SRCALPHA)
        rect = self.image.get_rect(center=(128, 128))
        image.blit(self.image, rect)

        try:
            os.remove(f"Graphics/Towers/Temp/{self.building_name} - 0.ico")
        except FileNotFoundError:
            pass

        pygame.image.save(image, f"Graphics/Towers/Temp/{self.building_name} - 0.png")

        img = Image.open(f"Graphics/Towers/Temp/{self.building_name} - 0.png")
        img.save(f"Graphics/Towers/Temp/{self.building_name} - 0.ico", format="ICO", sizes=[(256, 256)])

        os.remove(f"Graphics/Towers/Temp/{self.building_name} - 0.png")

        set_folder_icon(self.folder_path, f"Graphics/Towers/Temp/{self.building_name} - 0.ico")
        self.icon_updated = False

        self.target_points = {(self.rect.center, self)}

    def choose_attack_sfx(self):
        path = os.path.join("SoundEffects/Towers/Gunshots", choice(self.attack_sound_effects))
        self.attack_SFX = pygame.mixer.Sound(path)

        self.attack_SFX.set_volume(0.7)

    def choose_death_sfx(self):
        sfx_path = os.path.join("SoundEffects/Towers/Death", choice(self.death_sound_effects))
        self.death_SFX = pygame.mixer.Sound(sfx_path)

        self.death_SFX.set_volume(3)

    def get_closest_target(self, enemies):
        closest_enemy_dist = None
        distance = None

        for enemy in enemies:
            vector2_dist = enemy.rect.center - self.pos
            dist = sqrt(abs(vector2_dist[0])**2 + abs(vector2_dist[1])**2)

            if not closest_enemy_dist:
                closest_enemy_dist = dist
                distance = vector2_dist
            elif dist < closest_enemy_dist:
                closest_enemy_dist = dist
                distance = vector2_dist

        return distance

    def check_death(self):
        if self.health > 0:
            return

        towers.remove(self)
        UI.ui_elements.remove(self.health_bar)

        folder = os.path.join(os.path.join(os.environ['USERPROFILE']), 'OneDrive', "Desktop", self.name)
        remove_folder(folder)

        self.choose_death_sfx()
        self.death_SFX.play()

    def check_health(self):
        self.health_bar.pos = (self.pos[0] + Settings.ICON_WIDTH//2, self.pos[1] - Settings.ICON_HEIGHT//4)
        self.health_bar.fill_value = self.health

        self.check_death()

    def rotate_tower(self):
        rounded_angle = int(self.angle)

        if f"{self.building_name}-{rounded_angle}.ico" not in temp_icons:
            rotated_image = pygame.transform.rotate(self.image, 180+rounded_angle)

            image = pygame.Surface((256, 256), pygame.SRCALPHA)
            rect = rotated_image.get_rect(center=(128, 128))

            image.blit(rotated_image, rect)

            pygame.image.save(image, f"Graphics/Towers/Temp/{self.building_name} - {rounded_angle}.png")

            img = Image.open(f"Graphics/Towers/Temp/{self.building_name} - {rounded_angle}.png")
            img.save(f"Graphics/Towers/Temp/{self.building_name} - {rounded_angle}.ico",
                     format="ICO", sizes=[(256, 256)])

            os.remove(f"Graphics/Towers/Temp/{self.building_name} - {rounded_angle}.png")
            set_folder_icon(self.folder_path, f"Graphics/Towers/Temp/{self.building_name} - {rounded_angle}.ico")

        set_folder_icon(self.folder_path, f"Graphics/Towers/Temp/{self.building_name} - {rounded_angle}.ico")
        self.icon_updated = True

    def get_angle(self, dist):
        self.angle = 180 + degrees(atan2(dist.x, dist.y))

    def attack(self):
        Bullets.bullets.append(Bullets.CannonBall(self.rect.center, self.angle, self.power))

        self.choose_attack_sfx()
        self.attack_SFX.play()

    def update_icon(self, fps):
        if self.icon_updated:
            return

        self.time_since_start += 1 / fps

        if self.time_since_start >= 3:
            try:
                os.remove(f"Graphics/Towers/Temp/{self.building_name} - 0.ico")
            except FileNotFoundError:
                pass

            image = pygame.Surface((256, 256), pygame.SRCALPHA)
            rect = self.image.get_rect(center=(128, 128))
            image.blit(self.image, rect)

            pygame.image.save(image, f"Graphics/Towers/Temp/{self.building_name} - 0.png")

            img = Image.open(f"Graphics/Towers/Temp/{self.building_name} - 0.png")
            img.save(f"Graphics/Towers/Temp/{self.building_name} - 0.ico", format="ICO", sizes=[(256, 256)])
            temp_icons.append(f"{self.building_name} - 0.ico")

            os.remove(f"Graphics/Towers/Temp/{self.building_name} - 0.png")

            set_folder_icon(self.folder_path, f"Graphics/Towers/Temp/{self.building_name} - 0.ico")
            self.icon_updated = True

    def update(self, fps, enemies, *args, **kwargs):
        self.check_health()
        self.update_icon(fps)

        self.target_points.clear()
        self.target_points.add((self.rect.center, self))

        self.last_attack += 1 / fps

        if self.last_attack >= self.attack_rate * 0.7:
            distance = self.get_closest_target(enemies)

            if distance is None:
                self.last_attack = 0
                self.is_rotated = False

                return

            if not self.is_rotated:
                self.get_angle(distance)

                self.rotate_tower()
                self.is_rotated = True

            if self.last_attack >= self.attack_rate:
                self.attack()

                self.last_attack = 0
                self.is_rotated = False


class EmptyBuilding:
    def __init__(self, folder_path, name, pos, raw_pos):
        self.image_path = r"Graphics/Towers/EmptyBuilding/Empty-Building.jpg"
        self.building_name = "Empty Building"

        self.folder_path = folder_path
        self.name = name

        self.full_health = 50
        self.health = self.full_health

        self.pos = pygame.Vector2(pos)
        self.raw_pos = pygame.Vector2(raw_pos)

        self.image = pygame.Surface((Settings.ICON_WIDTH, Settings.ICON_HEIGHT))
        self.rect = self.image.get_rect(topleft=self.pos)

        self.health_bar = UI.Bar((self.pos[0] + Settings.ICON_WIDTH//2, self.pos[1] - Settings.ICON_HEIGHT//4),
                                 "GREEN", self.full_health, self.health, 0.5, group=towers, owner=self)
        UI.ui_elements.append(self.health_bar)

        self.death_sound_effects = os.listdir("SoundEffects/Towers/Death")
        self.death_SFX = None

        self.icon_updated = False

        self.time_since_start = 0

        img = Image.open(self.image_path)
        img.save(f"Graphics/Towers/Temp/{self.building_name} - {id(self)}.ico", format="ICO", sizes=[(256, 256)])
        set_folder_icon(self.folder_path, f"Graphics/Towers/Temp/{self.building_name} - {id(self)}.ico")

        temp_icons.append(f"{self.building_name} - {id(self)}.ico")

        self.tower_tokens = {"Cannon.png": Cannon,
                             "Wall Post.png": WallPost}
        self.special_tower_tokens = {"Wall Post - Parent= (.*).png": (WallPost.create_as_child, WallPost)}

        self.target_points = {(self.rect.center, self)}

    def choose_death_sfx(self):
        sfx_path = os.path.join("SoundEffects/Towers/Death", choice(self.death_sound_effects))
        self.death_SFX = pygame.mixer.Sound(sfx_path)

        self.death_SFX.set_volume(3)

    def check_death(self):
        if self.health > 0:
            return

        towers.remove(self)
        UI.ui_elements.remove(self.health_bar)

        folder = os.path.join(os.path.join(os.environ['USERPROFILE']), 'OneDrive', "Desktop", self.name)
        remove_folder(folder)

        self.choose_death_sfx()
        self.death_SFX.play()

    def check_health(self):
        self.health_bar.pos = (self.pos[0] + Settings.ICON_WIDTH//2, self.pos[1] - Settings.ICON_HEIGHT//4)
        self.health_bar.fill_value = self.health
        self.check_death()

    def update_icon(self, fps):
        if self.icon_updated:
            return

        self.time_since_start += 1 / fps

        if self.time_since_start >= 3:
            try:
                os.remove(f"Graphics/Towers/Temp/{self.building_name} - {id(self)}.ico")
            except FileNotFoundError:
                pass

            img = Image.open(self.image_path)
            img.save(f"Graphics/Towers/Temp/{self.building_name} - {id(self)}.ico", format="ICO", sizes=[(256, 256)])

            set_folder_icon(self.folder_path, f"Graphics/Towers/Temp/{self.building_name} - {id(self)}.ico")

            self.icon_updated = True

    def check_tower_tokens(self):
        try:
            folder_contents = os.listdir(self.folder_path)
        except FileNotFoundError:
            return

        for name, cls in self.tower_tokens.items():
            if name in folder_contents:
                os.remove(os.path.join(self.folder_path, name))

                if Money.money >= cls.COST:
                    towers.append(cls(self.folder_path, self.name, self.pos, self.raw_pos))

                    towers.remove(self)

                    temp_icons.remove(f"Empty Building - {id(self)}.ico")

                    os.remove(f"Graphics/Towers/Temp/Empty Building - {id(self)}.ico")

                    Money.money -= cls.COST
                    Money.update_money_text()
                    return

        for name, (cls_creator, cls) in self.special_tower_tokens.items():
            for file_name in folder_contents:
                file_id = search(name, file_name)
                if not file_id:
                    continue

                os.remove(os.path.join(self.folder_path, file_id.group(0)))

                if Money.money >= cls.COST:
                    towers.append(cls_creator(file_name, self.folder_path, self.name, self.pos, self.raw_pos))

                    towers.remove(self)
                    temp_icons.remove(f"Empty Building - {id(self)}.ico")
                    os.remove(f"Graphics/Towers/Temp/Empty Building - {id(self)}.ico")

                    Money.money -= cls.COST
                    Money.update_money_text()
                    return

    def update(self, fps, *args, **kwargs):
        self.update_icon(fps)
        self.check_tower_tokens()
        self.check_health()

        self.target_points.clear()
        self.target_points.add((self.rect.center, self))


class TownHall:
    def __init__(self, folder_path, name, pos, raw_pos):
        self.image_path = r"Graphics/Towers/TownHall/Town-hall.png"

        self.building_name = "TownHall"

        self.folder_path = folder_path
        self.name = name

        self.full_health = 300
        self.health = self.full_health

        self.pos = pygame.Vector2(pos)
        self.raw_pos = pygame.Vector2(raw_pos)

        self.image = pygame.Surface((Settings.ICON_WIDTH, Settings.ICON_HEIGHT))
        self.rect = self.image.get_rect(topleft=self.pos)

        self.health_bar = UI.Bar((self.pos[0] + Settings.ICON_WIDTH//2, self.pos[1] - Settings.ICON_HEIGHT//4),
                                 "GREEN", self.full_health, self.health, Settings.SCREEN_SCALED, group=towers, owner=self)
        UI.ui_elements.append(self.health_bar)

        self.death_sound_effects = os.listdir("SoundEffects/Towers/Death")
        self.death_SFX = None

        self.icon_updated = False

        self.time_since_start = 0

        img = Image.open(self.image_path)
        img.save(f"Graphics/Towers/Temp/{self.building_name} - {id(self)}.ico", format="ICO", sizes=[(256, 256)])
        set_folder_icon(self.folder_path, f"Graphics/Towers/Temp/{self.building_name} - {id(self)}.ico")

        self.tower_tokens_paths = {"Cannon.png": r"Graphics/Towers/Cannon/Cannon.png",
                                   "Wall Post.png": r"Graphics/Towers/Wall/Wall Post.png"}

        self.target_points = {(self.rect.center, self)}

    def choose_death_sfx(self):
        sfx_path = os.path.join("SoundEffects/Towers/Death", choice(self.death_sound_effects))
        self.death_SFX = pygame.mixer.Sound(sfx_path)

        self.death_SFX.set_volume(3)

    def check_death(self):
        if self.health > 0:
            return

        towers.remove(self)
        UI.ui_elements.remove(self.health_bar)

        folder = os.path.join(os.path.join(os.environ['USERPROFILE']), 'OneDrive', "Desktop", self.name)
        remove_folder(folder)

        self.choose_death_sfx()
        self.death_SFX.play()

    def check_health(self):
        self.health_bar.pos = (self.pos[0] + Settings.ICON_WIDTH//2, self.pos[1] - Settings.ICON_HEIGHT//4)
        self.health_bar.fill_value = self.health
        self.check_death()

    def update_icon(self, fps):
        if self.icon_updated:
            return

        self.time_since_start += 1 / fps

        if self.time_since_start >= 3:
            try:
                os.remove(f"Graphics/Towers/Temp/{self.building_name} - {id(self)}.ico")
            except FileNotFoundError:
                pass

            img = Image.open(self.image_path)
            img.save(f"Graphics/Towers/Temp/{self.building_name} - {id(self)}.ico", format="ICO", sizes=[(256, 256)])

            temp_icons.append(f"{self.building_name} - {id(self)}.ico")

            set_folder_icon(self.folder_path, f"Graphics/Towers/Temp/{self.building_name} - {id(self)}.ico")

            self.icon_updated = True

    def update_tower_tokens(self):
        try:
            folder_contents = os.listdir(self.folder_path)
        except FileNotFoundError:
            return

        for name, path in self.tower_tokens_paths.items():
            if name not in folder_contents:
                copy(path, self.folder_path)

    def update(self, fps, *args, **kwargs):
        self.update_icon(fps)
        self.update_tower_tokens()
        self.check_health()

        self.target_points.clear()
        self.target_points.add((self.rect.center, self))


class Cannon(AttackTower):
    COST = 250

    def __init__(self, folder_path, name, pos, raw_pos):
        super().__init__(folder_path, name, "Cannon", "Graphics/Towers/Cannon/Cannon.png", pos, 100, raw_pos)

        self.image = pygame.image.load("Graphics/Towers/Cannon/Cannon.png").convert_alpha()


class WallConnector:
    def __init__(self, post1, post2, target_points_lst):
        self.image = None
        self.rect = None
        self.target_points = target_points_lst

        post1.health /= 2
        post1.full_health -= post1.health

        post2.health /= 2
        post2.full_health -= post1.health

        self.post1 = post1
        self.post2 = post2

        self.full_health = post1.health / 2 + post2.health / 2
        self.health = self.full_health

        mid_x = (self.post1.rect.center[0] + self.post2.rect.center[0]) / 2
        mid_y = (self.post1.rect.center[1] + self.post2.rect.center[1]) / 2
        self.pos = (mid_x, mid_y)

        self.health_bar = UI.Bar((self.pos[0] + Settings.ICON_WIDTH//2, self.pos[1] - Settings.ICON_HEIGHT//4),
                                 "GREEN", self.full_health, self.health, 0.5, group=towers, owner=self)
        UI.ui_elements.append(self.health_bar)

        self.brick_surf = pygame.transform.rotozoom(pygame.image.load("Graphics/Towers/Wall/Wall Brick.png").convert(),
                                                    0, Settings.SCREEN_SCALED)

        self.brick_size = self.brick_surf.get_size()
        self.surf = None
        self.rotation = 0
        self.mask = None

    def update_connection(self):
        dist_vector, dist_magnitude = MathExtented.get_distance_of_two_points(
            pygame.Vector2(self.post1.rect.center), pygame.Vector2(self.post2.rect.center))
        self.rotation = MathExtented.get_angle_vector2(dist_vector) + 90

        self.surf = pygame.Surface((dist_magnitude, self.brick_size[1]), pygame.SRCALPHA)

        n_bricks = dist_magnitude / self.brick_size[0]

        mid_x = (self.post1.rect.center[0] + self.post2.rect.center[0]) // 2
        mid_y = (self.post1.rect.center[1] + self.post2.rect.center[1]) // 2
        self.pos = (mid_x + Settings.ICON_WIDTH//2, mid_y + Settings.ICON_HEIGHT//2)

        for i in range(ceil(n_bricks)):
            self.surf.blit(self.brick_surf, pygame.Rect(self.brick_size[0] * i, 0, *self.brick_size))

        self.surf = pygame.transform.rotate(self.surf, self.rotation)

        self.target_points.clear()

        for i in range(ceil(n_bricks)):
            half_n_bricks = (ceil(n_bricks) / 2)
            new_point = MathExtented.rotate_point(0, 0, self.rotation,
                                                  self.brick_size[0] * i
                                                  - half_n_bricks * self.brick_size[0] + self.brick_size[0] / 2, 0)

            self.target_points.add(((new_point[0] + self.pos[0], new_point[1] + self.pos[1]), self))

        self.mask = pygame.mask.from_surface(self.surf)

    def draw(self, screen):
        self.update_connection()

        screen.blit(self.surf, self.surf.get_rect(center=self.pos))


class WallPost:
    COST = 150

    def __init__(self, folder_path, name, pos, raw_pos, parent=None):
        self.image_path = r"Graphics/Towers/Wall/Wall Post.png"

        self.building_name = "WallPost"

        self.folder_path = folder_path
        self.name = name

        self.full_health = 200
        self.health = self.full_health

        self.pos = pygame.Vector2(pos)
        self.raw_pos = pygame.Vector2(raw_pos)

        self.image = pygame.Surface((Settings.ICON_WIDTH, Settings.ICON_HEIGHT))
        self.rect = self.image.get_rect(topleft=self.pos)

        self.health_bar = UI.Bar((self.pos[0] + Settings.ICON_WIDTH//2, self.pos[1] - Settings.ICON_HEIGHT//4),
                                 "GREEN", self.full_health, self.health, 0.5, group=towers, owner=self)
        UI.ui_elements.append(self.health_bar)

        self.death_sound_effects = os.listdir("SoundEffects/Towers/Death")
        self.death_SFX = None

        self.icon_updated = False

        self.time_since_start = 0

        img = Image.open(self.image_path)
        img.save(f"Graphics/Towers/Temp/{self.building_name} - {id(self)}.ico", format="ICO", sizes=[(256, 256)])
        set_folder_icon(self.folder_path, f"Graphics/Towers/Temp/{self.building_name} - {id(self)}.ico")

        self.connector_token_path = "Graphics/Towers/Wall/Wall Post.png"
        self.add_connector_token()

        self.parent = parent
        self.is_child = parent is not None

        self.target_points = {(self.rect.center, self)}

        self.connector = None
        if self.is_child:
            self.connector = WallConnector(self, parent, self.target_points)

    @staticmethod
    def create_as_child(token_name, folder_path, name, pos, raw_pos):
        parent_id = int(search("Parent= (.*).png", token_name).group(1))
        parent = [tower for tower in towers if id(tower) == parent_id][0]

        return WallPost(folder_path, name, pos, raw_pos, parent)

    def add_connector_token(self):
        if not os.path.exists(self.folder_path):
            return

        copy(self.connector_token_path, self.folder_path)
        os.rename(os.path.join(self.folder_path, "Wall Post.png"),
                  os.path.join(self.folder_path, f"Wall Post - Parent= {id(self)}.png"))

    def choose_death_sfx(self):
        sfx_path = os.path.join("SoundEffects/Towers/Death", choice(self.death_sound_effects))
        self.death_SFX = pygame.mixer.Sound(sfx_path)

        self.death_SFX.set_volume(3)

    def check_death(self):
        if self.health > 0:
            return

        towers.remove(self)
        UI.ui_elements.remove(self.health_bar)

        folder = os.path.join(os.path.join(os.environ['USERPROFILE']), 'OneDrive', "Desktop", self.name)
        remove_folder(folder)

        self.choose_death_sfx()
        self.death_SFX.play()

    def check_health(self):
        self.health_bar.pos = (self.pos[0] + Settings.ICON_WIDTH//2, self.pos[1] - Settings.ICON_HEIGHT//4)
        self.health_bar.max_value = self.full_health
        self.health_bar.fill_value = self.health
        self.check_death()

    def update_icon(self, fps):
        if self.icon_updated:
            return

        self.time_since_start += 1 / fps

        if self.time_since_start >= 3:
            try:
                os.remove(f"Graphics/Towers/Temp/{self.building_name} - {id(self)}.ico")
            except FileNotFoundError:
                pass

            img = Image.open(self.image_path)
            img.save(f"Graphics/Towers/Temp/{self.building_name} - {id(self)}.ico", format="ICO", sizes=[(256, 256)])

            temp_icons.append(f"{self.building_name} - {id(self)}.ico")

            set_folder_icon(self.folder_path, f"Graphics/Towers/Temp/{self.building_name} - {id(self)}.ico")

            self.icon_updated = True

    def update(self, fps, *args, **kwargs):
        self.update_icon(fps)
        self.check_health()

        if self.is_child:
            self.connector.draw(kwargs["screen"])

            self.target_points.add((self.rect.center, self))
