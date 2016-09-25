#!/usr/bin/env python
try:
    import sys
    from pygame_cards import card_sprite
    from pygame_cards import game_object
except ImportError as err:
    print "Fail loading a module in file:", __file__, "\n", err
    sys.exit(2)


class Card(game_object.GameObject):
    """ This class represents a card. """

    def __init__(self, suit, rank, pos, back_up=False):
        game_object.GameObject.__init__(self)
        self.suit = suit
        self.rank = rank
        self.sprite = card_sprite.CardSprite(suit, rank, pos, back_up)
        #self.back_sprite = card_sprite.CardBackSprite(pos)
        self.back_up = back_up

    def get_sprite(self):
        """ Returns card's spite object
        :return: card's sprite object
        """
        return self.sprite

    # def get_back_sprite(self):
    #     return self.back_sprite

    def render(self, screen):
        """ Renders the card's sprite on a screen passed in argument
        :param screen: screen to render the card's sprite on
        """
        self.sprite.render(screen)

    def flip(self):
        """ Flips the card from face-up to face-down and vice versa """
        self.back_up = not self.back_up
        self.sprite.flip()

    def is_clicked(self, pos):
        """ Checks if mouse click is on card
        :param pos: tuple with coordinates of mouse click (x, y)
        :return: True if card is clicked, False otherwise
        """
        return self.sprite.is_clicked(pos)

    def unclick(self):
        """ Marks card as unclicked, i.e. it won't stick to the mouse cursor """
        self.sprite.clicked = False

    def check_mouse(self, pos, down):
        """ Checks if mouse event affects the card and if so processes the event.
        :param pos: tuple with coordinates of mouse event (x, y)
        :param down: boolean, should be True for mouse down event, False for mouse up event
        :return: True if passed mouse event affects the card, False otherwise.

        """
        return self.sprite.check_mouse(pos, down)

    def check_collide(self, card_=None, pos=None):
        """ Checks if current card's sprite collides with other card's sprite, or with
        an rectangular area with size of a card. Parameters card and pos are mutually exclusive.
        :param card_: Card object to check collision with
        :param pos: tuple with coordinates (x,y) - top left corner of area to check collision with
        :return: True if cards/card and area collide, False otherwise
        """
        if card_ is not None:
            return self.sprite.check_card_collide(card_.sprite)
        elif pos is not None:
            return self.sprite.check_area_collide(pos)

    def set_pos(self, pos):
        """ Sets position of the card's sprite
        :param pos: tuple with coordinates (x, y) where the top left corner of the card
                    should be placed.
        """
        self.sprite.pos = pos
        #self.back_sprite.set_pos(pos)

    def offset_pos(self, pos):
        """ Move the card's position by the specified offset
        :param pos: tuple with coordinates (x, y) of the offset to move card
        """
        self.sprite.offset_pos(pos)
        #self.back_sprite.offset_pos(pos)
