#!/usr/bin/env python
from __future__ import division
try:
    import sys
    import os
    import math
    import pygame

    from pygame_cards import globals, enums
except ImportError as err:
    print "Fail loading a module: %s", err
    sys.exit(2)


def load_img(path):
    if __debug__:
        # In debug mode use full file path
        directory = os.path.dirname(__file__)
        return os.path.join(directory, path)
    else:
    # In production environment use relative path from json
        return path


class AbstractPygameCardSprite(pygame.sprite.Sprite):
    """ Abstract base class for Card sprite with pygame routines implemented in default methods. """

    def __init__(self, pos):
        self.rect = [pos[0], pos[1], 0, 0]
        self.mouse_offset = [0, 0]
        self.clicked = False
        self.image = None  # Placeholder for card sprite

    @property
    def pos(self):
        return self.rect[0], self.rect[1]

    @pos.setter
    def pos(self, pos):
        self.rect[0] = pos[0]
        self.rect[1] = pos[1]

    def offset_pos(self, pos):
        self.rect[0] = self.rect[0] + pos[0]
        self.rect[1] = self.rect[1] + pos[1]

    def get_rect(self):
        return self.image.get_rect()

    def update(self):
        if self.clicked:
            self.rect[0] = pygame.mouse.get_pos()[0] - self.mouse_offset[0]
            self.rect[1] = pygame.mouse.get_pos()[1] - self.mouse_offset[1]

    def render(self, screen):
        self.update()
        screen.blit(*self.get_render_tuple())

    def get_render_tuple(self):
        return self.image, (self.rect[0], self.rect[1])

    def is_clicked(self, p):
        return p[0] > self.rect[0] and p[0] < (self.rect[0] + self.get_rect()[2]) and\
                p[1] > self.rect[1] and p[1] < (self.rect[1] + self.get_rect()[3])

    def check_mouse(self, p, down):
        if self.is_clicked(p):
            if isinstance(down, bool):
                self.clicked = down
            self.mouse_offset[0] = p[0] - self.rect[0]
            self.mouse_offset[1] = p[1] - self.rect[1]
            return True
        else:
            return False

    def check_card_collide(self, sprite):
        rect = pygame.Rect(self.rect)
        return rect.colliderect(sprite.rect)

    def check_area_collide(self, pos):
        rect1 = pygame.Rect(self.rect)
        rect2 = pygame.Rect((pos[0], pos[1], self.rect[2], self.rect[3]))
        return rect1.colliderect(rect2)


class CardSprite(AbstractPygameCardSprite):
    """ Concrete pygame Card sprite class. Represents both front and back card's sprites. """

    def __init__(self, suit, rank, pos, back_up=False):
        AbstractPygameCardSprite.__init__(self, pos)
        self.suit = suit
        self.rank = rank
        temp_image = pygame.image.load(load_img(self.get_image_path(self.suit, self.rank))).convert_alpha()
        self.image = pygame.transform.scale(temp_image, globals.settings_json["card"]["size"])
        self.rect = self.image.get_rect()
        self.rect[0] = pos[0]
        self.rect[1] = pos[1]

        back_img_path = globals.settings_json["card"]["back_sprite_file"]
        temp_image = pygame.image.load(load_img(back_img_path)).convert_alpha()
        self.back_image = pygame.transform.scale(temp_image, globals.settings_json["card"]["size"])
        self.back_up = back_up

    def get_render_tuple(self):
        if self.back_up:
            return self.back_image, (self.rect[0], self.rect[1])
        else:
            return self.image, (self.rect[0], self.rect[1])

    def flip(self):
        self.back_up = not self.back_up

    @staticmethod
    def get_image_path(s, r):
        path = globals.settings_json["card"]["front_sprite_path"]

        if r == enums.Rank.two:
            path += "2_of_"
        elif r == enums.Rank.three:
            path += "3_of_"
        elif r == enums.Rank.four:
            path += "4_of_"
        elif r == enums.Rank.five:
            path += "5_of_"
        elif r == enums.Rank.six:
            path += "6_of_"
        elif r == enums.Rank.seven:
            path += "7_of_"
        elif r == enums.Rank.eight:
            path += "8_of_"
        elif r == enums.Rank.nine:
            path += "9_of_"
        elif r == enums.Rank.ten:
            path += "10_of_"
        elif r == enums.Rank.jack:
            path += "jack_of_"
        elif r == enums.Rank.queen:
            path += "queen_of_"
        elif r == enums.Rank.king:
            path += "king_of_"
        elif r == enums.Rank.ace:
            path += "ace_of_"

        if s == enums.Suit.hearts:
            path += "hearts"
        elif s == enums.Suit.diamonds:
            path += "diamonds"
        elif s == enums.Suit.clubs:
            path += "clubs"
        elif s == enums.Suit.spades:
            path += "spades"

        # use images with pictures for jack, queen, king
        if enums.Rank.ten < r < enums.Rank.ace:
            path += "2.png"
        else:
            path += ".png"

        return path

# class CardBackSprite(AbstractPygameCardSprite):
#     def __init__(self, pos):
#         AbstractPygameCardSprite.__init__(self, pos)
#         back_img_path = "img/back-side.png"
#         temp_image = pygame.image.load(load_img(back_img_path)).convert()
#         #w = temp_image.get_rect()[2]
#         #h = temp_image.get_rect()[3]
#         self.image = pygame.transform.scale(temp_image, globals.Size.card)


class SpriteMove:
    def __init__(self, sprites, dest_pos, speed=None):
        self.sprites = sprites
        self.dest_pos = dest_pos
        for sprite in self.sprites:
            sprite.start_pos = sprite.pos
            sprite.angle = math.atan2(dest_pos[1] - sprite.start_pos[1], dest_pos[0] - sprite.start_pos[0])
            sprite.distance = SpriteMove.calc_distance(dest_pos, sprite.start_pos)
            if speed is None:
                sprite.speed = globals.settings_json["card"]["move_speed"]
            else:
                sprite.speed = speed
            sprite.completed = False

    @staticmethod
    def calc_distance(p1, p2):
        return math.sqrt(math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2))

    # Returns True is move to destination position is completed, otherwise returns False
    def update(self):
        for sprite in self.sprites:
            new_pos = sprite.pos[0] + sprite.speed * math.cos(sprite.angle), \
                      sprite.pos[1] + sprite.speed * math.sin(sprite.angle)
            d = SpriteMove.calc_distance(new_pos, sprite.start_pos)
            if d < sprite.distance:
                sprite.pos = new_pos
            else:
                sprite.pos = self.dest_pos
                sprite.completed = True

    def is_completed(self):
        result = True
        for sprite in self.sprites:
            result = result and sprite.completed
        return result
