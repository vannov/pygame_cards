#!/usr/bin/env python
from __future__ import division
try:
    import sys
    import os
    import math
    import pygame

    from pygame_cards import enums
except ImportError as err:
    print "Fail loading a module in file:", __file__, "\n", err
    sys.exit(2)


def get_img_full_path(path):
    """ Checks if file can be found by path specified in the input. Returns the same as input
    if can find, otherwise joins current directory full path with path from input and returns it.
    :param path: Relative of full path to the image.
    :return: Relative of full path to the image (joined with path to current directory if needed).
    """
    if os.path.isfile(path):
        return path
    else:
        directory = os.path.dirname(__file__)
        new_path = os.path.join(directory, path)
        if os.path.isfile(new_path):
            return new_path
        else:
            raise IOError("File not found: " + path)


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

    def is_clicked(self, pos):
        return (pos[0] > self.rect[0] and pos[0] < (self.rect[0] + self.get_rect()[2]) and
                pos[1] > self.rect[1] and pos[1] < (self.rect[1] + self.get_rect()[3]))

    def check_mouse(self, pos, down):
        if self.is_clicked(pos):
            if isinstance(down, bool):
                self.clicked = down
            self.mouse_offset[0] = pos[0] - self.rect[0]
            self.mouse_offset[1] = pos[1] - self.rect[1]
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
    """ Concrete pygame Card sprite class. Represents both front and back card's sprites.

    Attributes:
        card_json - The 'card' node of the settings.json. Data can be accessed via [] operator,
                    for example: CardsHolder.card_json["size"][0]
    """

    card_json = None

    def __init__(self, suit, rank, pos, back_up=False):
        if CardSprite.card_json is None:
            raise ValueError('CardSprite.card_json is not initialized')
        AbstractPygameCardSprite.__init__(self, pos)

        temp_image = pygame.image.load(get_img_full_path(
            self.get_image_path(suit, rank))).convert_alpha()
        self.image = pygame.transform.scale(temp_image, CardSprite.card_json["size"])
        self.rect = self.image.get_rect()
        self.rect[0] = pos[0]
        self.rect[1] = pos[1]

        back_img_path = CardSprite.card_json["back_sprite_file"]
        temp_image = pygame.image.load(get_img_full_path(back_img_path)).convert_alpha()
        self.back_image = pygame.transform.scale(temp_image, CardSprite.card_json["size"])
        self.back_up = back_up

    def get_render_tuple(self):
        if self.back_up:
            return self.back_image, (self.rect[0], self.rect[1])
        else:
            return self.image, (self.rect[0], self.rect[1])

    def flip(self):
        self.back_up = not self.back_up

    @staticmethod
    def get_image_path(suit, rank):
        path = CardSprite.card_json["front_sprite_path"]

        if rank == enums.Rank.two:
            path += "2_of_"
        elif rank == enums.Rank.three:
            path += "3_of_"
        elif rank == enums.Rank.four:
            path += "4_of_"
        elif rank == enums.Rank.five:
            path += "5_of_"
        elif rank == enums.Rank.six:
            path += "6_of_"
        elif rank == enums.Rank.seven:
            path += "7_of_"
        elif rank == enums.Rank.eight:
            path += "8_of_"
        elif rank == enums.Rank.nine:
            path += "9_of_"
        elif rank == enums.Rank.ten:
            path += "10_of_"
        elif rank == enums.Rank.jack:
            path += "jack_of_"
        elif rank == enums.Rank.queen:
            path += "queen_of_"
        elif rank == enums.Rank.king:
            path += "king_of_"
        elif rank == enums.Rank.ace:
            path += "ace_of_"

        if suit == enums.Suit.hearts:
            path += "hearts"
        elif suit == enums.Suit.diamonds:
            path += "diamonds"
        elif suit == enums.Suit.clubs:
            path += "clubs"
        elif suit == enums.Suit.spades:
            path += "spades"

        # use images with pictures for jack, queen, king
        if enums.Rank.ten < rank < enums.Rank.ace:
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


class SpriteMove(object):
    """
    Class that animates a card move. Can be used to animate automatic cards' moves,
    for example during cards dealing.
    """
    def __init__(self, sprites, dest_pos, speed=None):
        """ Initializes an object of SpriteMove class.
        :param sprites: list of card sprites to be moved
        :param dest_pos: tuple with coordinates (x,y) of destination position
        :param speed: integer number, on how many pixels card(s) should move per frame.
                    If not specified (None), "move_speed" value from the config json is used.
        """
        self.sprites = sprites
        self.dest_pos = dest_pos
        for sprite in self.sprites:
            sprite.start_pos = sprite.pos
            sprite.angle = math.atan2(dest_pos[1] - sprite.start_pos[1],
                                      dest_pos[0] - sprite.start_pos[0])
            sprite.distance = SpriteMove.calc_distance(dest_pos, sprite.start_pos)
            if speed is None:
                sprite.speed = CardSprite.card_json["move_speed"]
            else:
                sprite.speed = speed
            sprite.completed = False

    @staticmethod
    def calc_distance(point1, point2):
        """ Calculates distance between two points.
        :param point1: tuple (x, y) with coordinates of the first point
        :param point2: tuple (x, y) with coordinates of the second point
        :return: distance between two points in pixels
        """
        return math.sqrt(math.pow(point1[0] - point2[0], 2) + math.pow(point1[1] - point2[1], 2))

    def update(self):
        """
        Updates sprite(s) position. IMPORTANT: this method should be executed in an endless loop
        during all lifetime of SpriteMove object in order for animation to be smooth.
        :return: True is move to destination position is completed, otherwise returns False.
        """
        for sprite in self.sprites:
            new_pos = (sprite.pos[0] + sprite.speed * math.cos(sprite.angle),
                       sprite.pos[1] + sprite.speed * math.sin(sprite.angle))
            distance = SpriteMove.calc_distance(new_pos, sprite.start_pos)
            if distance < sprite.distance:
                sprite.pos = new_pos
            else:
                sprite.pos = self.dest_pos
                sprite.completed = True

    def is_completed(self):
        """
        Checks if animation is completed.
        :return: True is sprite(s) reached the destination point. False otherwise.
        """
        result = True
        for sprite in self.sprites:
            result = result and sprite.completed
        return result
