import pygame
from pygame import Vector2
from math import sqrt, degrees, atan2, sin, cos, pi
from os import listdir, path
from random import choice

from Animations import Animation
import Settings

import UI
from MathExtented import rotate_point

import Money

enemies = []


class Enemy:
    def __init__(self, fps, pos, speed, power, health, targets, reward):
        self.FPS = fps
        self.pos = Vector2(pos)
        self.speed = speed
        self.power = power

        self.reward = reward

        self.full_health = health
        self.health = health

        self.targets = targets

        self.image = None
        self.rect = None
        self.mask = None
        self.angle = 0

        self.attack_rate = 1
        self.last_attack = 0

        self.health_bar = UI.Bar((0, 0), "RED", self.full_health, self.health, 0.4, group=enemies, owner=self)
        UI.ui_elements.append(self.health_bar)

        self.default_size = None

        self.name = None

        self.walk_sound_effects = listdir("SoundEffects/Enemy/Footsteps")
        self.walk_SFX = None
        self.walk_sfx_last_played = 0
        self.walk_sfx_rate = 2 / self.speed

        self.attack_sound_effects = listdir("SoundEffects/Enemy/Attack")
        self.attack_SFX = None

        self.death_sound_effects = listdir("SoundEffects/Enemy/Death")
        self.death_SFX = None

    def choose_walk_sfx(self):
        sfx_path = path.join("SoundEffects/Enemy/Footsteps", choice(self.walk_sound_effects))
        self.walk_SFX = pygame.mixer.Sound(sfx_path)

        self.walk_SFX.set_volume(0.4)

    def choose_attack_sfx(self):
        sfx_path = path.join("SoundEffects/Enemy/Attack", choice(self.attack_sound_effects))
        self.attack_SFX = pygame.mixer.Sound(sfx_path)

        self.attack_SFX.set_volume(0.7)

    def choose_death_sfx(self):
        sfx_path = path.join("SoundEffects/Enemy/Death", choice(self.death_sound_effects))
        self.death_SFX = pygame.mixer.Sound(sfx_path)

        self.death_SFX.set_volume(3)

    def get_closest_target(self):
        closest_target_dist = None
        closest_target = None
        distance = None

        for target in self.targets:
            for target_point, target_cls in target.target_points:
                vector2_dist = target_point - self.pos
                dist = sqrt(abs(vector2_dist[0])**2 + abs(vector2_dist[1])**2)

                if not closest_target_dist:
                    closest_target_dist = dist
                    closest_target = target_cls
                    distance = vector2_dist
                elif dist < closest_target_dist:
                    closest_target_dist = dist
                    closest_target = target_cls
                    distance = vector2_dist

        return distance, closest_target

    def attack_collision(self, target):
        self.last_attack += 1 / Settings.FPS

        if self.last_attack >= self.attack_rate:
            target.health -= self.power
            self.last_attack = 0

            self.choose_attack_sfx()
            self.attack_SFX.play()

    def attack(self, target):
        if target.health <= 0:
            return

        if hasattr(target, "mask") and target.mask:
            offset = (self.pos[0] - target.pos[0], self.pos[1] - target.pos[1])
            if self.mask.overlap(target.mask, offset):

                self.attack_collision(target)

                return True

        elif hasattr(target, "rect") and target.rect:
            if self.rect.colliderect(target.rect):
                self.attack_collision(target)

                return True

    def check_death(self):
        if self.health <= 0:
            UI.ui_elements.remove(self.health_bar)
            enemies.remove(self)

            self.choose_death_sfx()
            self.death_SFX.play()

            Money.money += self.reward

    def check_health(self):
        self.health_bar.rotation = self.angle

        x, y = rotate_point(self.pos[0], self.pos[1], self.angle,
                            offset_x=0, offset_y=-self.default_size[1] / 2 - 20 * Settings.SCREEN_SCALED)

        self.health_bar.pos = (x, y)
        self.health_bar.fill_value = self.health / self.full_health * 100

        self.check_death()

    def update(self, screen, targets):
        self.check_health()
        self.draw(screen)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class GreenEnemy(Enemy):
    def __init__(self, fps, pos, speed, power, health, targets):
        super().__init__(fps, pos, speed, power, health, targets, 100)
        self.animation = Animation(r"Graphics\GreenEnemy",
                                   0.45, self.pos, True, self.FPS)

        self.image = self.animation.get_frame()
        self.rect = self.image.get_rect(center=self.pos)
        self.default_size = self.rect.size

    def update(self, screen, targets):
        self.check_health()
        self.targets = targets

        self.draw(screen)
        distance, target = self.get_closest_target()

        if target is None:
            return

        dist_magnitude = sqrt(abs(distance[0])**2 + abs(distance[1])**2)

        attacking = self.attack(target)

        if attacking:
            self.rect = self.image.get_rect(center=self.pos)
            return

        self.angle = 180 + degrees(atan2(distance.x, distance.y))

        self.image = pygame.transform.rotozoom(self.animation.get_frame(), self.angle, 1)

        self.walk_sfx_last_played += 1 / Settings.FPS
        if self.walk_sfx_last_played >= self.walk_sfx_rate:
            self.walk_sfx_last_played = 0

            self.choose_walk_sfx()
            self.walk_SFX.play()

        self.pos += (distance[0] / dist_magnitude * self.speed, distance[1] / dist_magnitude * self.speed)
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)
