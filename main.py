import os
from sys import exit as sys_exit
from shutil import move

import pygame

import Bullets
import Desktop
import Enemies
import Icons
import Miscellaneous
import Settings
import Towers
import UI
from Animations import Animation
from random import choice
import Money


class Game:
    def __init__(self, fps: int):
        pygame.display.set_mode((1, 1))
        pygame.display.set_caption("Desktop Games")

        Desktop.minimize_window("Desktop Games")

        Settings.FPS = fps
        self.CLOCK = pygame.time.Clock()

        Settings.SCREEN_SCALED = 0.4

        Settings.SCREEN_SIZE = Desktop.get_screen_size(multiplier=Settings.SCREEN_SCALED)
        Settings.SCREEN = pygame.Surface(Settings.SCREEN_SIZE)
        Settings.ICON_WIDTH = round(Settings.SCREEN_SIZE[0] / 1920 * Settings.ICON_WIDTH)
        Settings.ICON_HEIGHT = round(Settings.SCREEN_SIZE[1] / 1080 * Settings.ICON_HEIGHT)
        Settings.ICON_X_GAP = round(Settings.SCREEN_SIZE[0] / 1920 * Settings.ICON_X_GAP)
        Settings.ICON_Y_GAP = round(Settings.SCREEN_SIZE[1] / 1080 * Settings.ICON_Y_GAP)
        Settings.ICON_LEFT_GAP = round(Settings.SCREEN_SIZE[0] / 1920 * Settings.ICON_LEFT_GAP)
        Settings.ICON_TOP_GAP = round(Settings.SCREEN_SIZE[1] / 1080 * Settings.ICON_TOP_GAP)

        self.safe_zones_pos = ((0, 0), (0, 1), (0, 2), (0, 3), (0, 4))
        self.safe_zones = []

        self.set_safe_zones()
        self.set_vault()

        self.town_hall = None

        Towers.towers = []

        Enemies.enemies.append(Enemies.GreenEnemy(Settings.FPS,
                                                  (1600 * Settings.SCREEN_SCALED, 700 * Settings.SCREEN_SCALED),
                                                  10, 10, 100, Towers.towers))

        self.last_frame_towers = []

        self.background_surf = pygame.image.load("Graphics/Grass Field.jpg").convert()
        self.background_surf = pygame.transform.smoothscale(self.background_surf, Settings.SCREEN_SIZE)
        self.background_rect = self.background_surf.get_rect(topleft=(0, 0))

        self.particle_effects = []

    def set_safe_zones(self):
        self.safe_zones.clear()

        for pos in self.safe_zones_pos:
            self.safe_zones.append(Miscellaneous.SafeZone(
                (pos[0] * (Settings.ICON_WIDTH + Settings.ICON_X_GAP) + Settings.ICON_LEFT_GAP,
                 pos[1] * (Settings.ICON_HEIGHT + Settings.ICON_Y_GAP) + Settings.ICON_TOP_GAP)))

    def set_vault(self):
        vault_path = os.path.join(os.path.join(os.environ['USERPROFILE']), "Desktop", "VAULT")

        if os.listdir(vault_path):
            if input("Do you wish to clear the contents of the VAULT?").upper() != "YES":
                self.quit_game()

        Desktop.remove_folder_contents(vault_path)

        for pos, name in Icons.get_icon_positions().items():
            if pos in self.safe_zones_pos:
                continue

            full_path = os.path.join(os.path.join(os.environ['USERPROFILE']), "Desktop", name)

            move(full_path, vault_path)

    def update_towers(self):
        new_towers = []

        for pos, name in Icons.get_icon_positions().items():
            if pos in self.safe_zones_pos:
                continue

            if name == "VAULT":
                continue

            full_path = os.path.join(os.path.join(os.environ['USERPROFILE']), "Desktop", name)

            if not os.path.isdir(full_path):
                continue

            is_in_towers = False
            old_tower = None

            for tower in Towers.towers:
                if name == tower.name:
                    is_in_towers = True
                    old_tower = tower
                    break

            if is_in_towers:
                old_tower.pos = pygame.Vector2((pos[0] * (Settings.ICON_WIDTH + Settings.ICON_X_GAP) + Settings.ICON_LEFT_GAP,
                                                pos[1] * (Settings.ICON_HEIGHT + Settings.ICON_Y_GAP) + Settings.ICON_TOP_GAP))
                old_tower.rect.center = old_tower.pos
                new_towers.append(old_tower)
            else:
                new_towers.append(
                    Towers.EmptyBuilding(
                        full_path, name,
                        ((pos[0] * (Settings.ICON_WIDTH + Settings.ICON_X_GAP) + Settings.ICON_LEFT_GAP,
                          pos[1] * (Settings.ICON_HEIGHT + Settings.ICON_Y_GAP) + Settings.ICON_TOP_GAP)), pos))

        Towers.towers.clear()

        Towers.towers.extend(new_towers)

        self.last_frame_towers = new_towers

    def locate_town_hall(self):
        for pos, name in Icons.get_icon_positions().items():
            if pos in self.safe_zones_pos:
                continue

            if name == "VAULT":
                continue

            full_path = os.path.join(os.path.join(os.environ['USERPROFILE']), "Desktop", name)

            if not os.path.isdir(full_path):
                continue

            if os.listdir(full_path):
                continue

            self.town_hall = Towers.TownHall(
                full_path, name,
                ((pos[0] * (Settings.ICON_WIDTH + Settings.ICON_X_GAP) + Settings.ICON_LEFT_GAP,
                  pos[1] * (Settings.ICON_HEIGHT + Settings.ICON_Y_GAP) + Settings.ICON_TOP_GAP)), pos)

            Towers.towers.append(self.town_hall)
            return

    @staticmethod
    def quit_game():
        pygame.quit()
        sys_exit()

    @staticmethod
    def get_explosion_sfx():
        explosion_sound_effects = os.listdir("SoundEffects/Explosions")
        sfx_path = os.path.join("SoundEffects/Explosions", choice(explosion_sound_effects))
        explosion_sfx = pygame.mixer.Sound(sfx_path)

        explosion_sfx.set_volume(2)

        return explosion_sfx

    def bullet_enemy_collisions(self):
        for bullet in Bullets.bullets:
            hit = False

            for enemy in Enemies.enemies:
                if bullet.rect.colliderect(enemy):
                    hit = True

                    enemy.health -= bullet.power

                    enemy.pos += bullet.direction * bullet.power
                    self.particle_effects.append(
                        Animation("Graphics/Effects/Explosion", 1, bullet.pos, False, Settings.FPS, 1.25))
                    self.get_explosion_sfx().play()

            if hit:
                Bullets.bullets.remove(bullet)

    def main_loop(self):
        while True:
            if Desktop.get_view() != "LARGE":
                self.quit_game()

            if self.town_hall is None:
                self.locate_town_hall()
            else:
                self.update_towers()
                self.bullet_enemy_collisions()

            self.draw()

            self.CLOCK.tick(Settings.FPS)

    def draw_main(self):
        [zone.draw(Settings.SCREEN) for zone in self.safe_zones]
        [bullet.update(Settings.SCREEN) for bullet in Bullets.bullets]
        [enemy.update(Settings.SCREEN, Towers.towers) for enemy in Enemies.enemies]
        [tower.update(Settings.FPS, Enemies.enemies, screen=Settings.SCREEN) for tower in Towers.towers]
        [effect.play(Settings.SCREEN) for effect in self.particle_effects]
        [element.draw(Settings.SCREEN) for element in UI.ui_elements]
        Money.update_money_text()

    def draw_start(self):
        [zone.draw(Settings.SCREEN) for zone in self.safe_zones]
        UI.put_text(Settings.SCREEN, None, (Settings.SCREEN_SIZE[0] / 2, 0),
                    "Place the TOWN HALL by creating a folder", "GOLD", True, "midtop")

    def draw(self):
        Settings.SCREEN.blit(self.background_surf, self.background_rect)

        if self.town_hall is None:
            self.draw_start()
        else:
            self.draw_main()

        try:
            pygame.image.save(Settings.SCREEN, "Output.jpg")
            Desktop.set_background(os.path.join(os.getcwd(), "Output.jpg"))
        except pygame.error:
            print("Missed Frame!")


if __name__ == "__main__":
    pygame.init()

    Desktop.remove_folder_contents(os.path.abspath("Graphics/Towers/Temp"))

    game = Game(6)
    game.main_loop()
