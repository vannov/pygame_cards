#!/usr/bin/env python

try:
    import sys
    import os
    import math
    import pygame

    from pygame_cards import enums
except ImportError as err:
    print("Fail loading a module in file:", __file__, "\n", err)
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

    def render(self, screen):
        screen.blit(*self.get_render_tuple())

    def get_render_tuple(self):
        return self.image, (self.rect[0], self.rect[1])

    def is_clicked(self, pos):
        return (pos[0] > self.rect[0] and pos[0] < (self.rect[0] + self.get_rect()[2]) and
                pos[1] > self.rect[1] and pos[1] < (self.rect[1] + self.get_rect()[3]))

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
