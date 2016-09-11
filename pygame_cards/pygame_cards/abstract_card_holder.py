#!/usr/bin/env python
try:
    import sys
    #import abc
    import operator
    from random import shuffle

    from pygame_cards import game_object, card, globals, enums
except ImportError as err:
    print "Fail loading a module: %s", err
    sys.exit(2)


class AbstractCardsHolder(game_object.GameObject):
    """ Abstract card holder, from which a card can be grabbed and moved to a different cards holder.
    Ex.: a player (player's pile of cards), a deck of cards.
    """
    #__metaclass__ = abc.ABCMeta

    def __init__(self, pos=(0, 0), offset=(0, 0), grab_policy=enums.GrabPolicy.no_grab, min_cards=0, last_card_callback=None):
        """
        :param min_cards: minimum number of cards required for cards holder to exist (default 0)
        :param last_card_callback: function to be called once the last card is removed (default None)
        """
        self.cards = []
        game_object.GameObject.__init__(self, self.cards, grab_policy)
        self.min_cards = min_cards
        self.last_card_callback = last_card_callback
        self.pos = pos
        self.offset = offset

    def is_clicked(self, pos):
        """ Checks if a top card is clicked.
        :param pos: tuple with coordinates (x, y) - position of mouse click/screen touch.
        :return: True if top card is clicked, False otherwise
        """
        if len(self.cards) is not 0:
            if self.cards[-1].is_clicked(pos):
                return True
        elif pos[0] > self.pos[0] and pos[0] < (self.pos[0] + globals.settings_json["card"]["size"][0]) and\
            pos[1] > self.pos[1] and pos[1] < (self.pos[1] + globals.settings_json["card"]["size"][1]):
            return True
        else:
            return False

    def check_click(self, pos):
        """ Checks if a top card is clicked.
        :param pos: tuple with coordinates (x, y) - position of mouse click/screen touch.
        :return: True if top card is clicked, False otherwise
        """
        if len(self.cards) is not 0:
            if self.cards[-1].check_mouse(pos, True):
                return True
        return False

    def try_grab_card(self, pos):
        """ Tries to grab a card (or multiple cards) with a mouse click.
        :param pos: tuple with coordinates (x, y) - position of mouse click/screen touch.
        :return: List with Card object if grabbed or None if card cannot be grabbed or mouse click is out of the holder.
        """
        grabbed_cards = None
        if len(self.cards) > self.min_cards:
            if self.grab_policy == enums.GrabPolicy.can_single_grab:
                if self.check_click(pos):
                    grabbed_cards = [self.pop_top_card()]
            elif self.grab_policy == enums.GrabPolicy.can_multi_grab:
                index = -1
                for c in reversed(self.cards):
                    if c.back_up:
                        break
                    if c.check_mouse(pos, True):
                        index = self.cards.index(c)
                        break

                if index != -1:
                    grabbed_cards = [c for c in self.cards if self.cards.index(c) >= index]
                    grabbed_cards.reverse()
                    self.cards[:] = [c for c in self.cards if self.cards.index(c) < index]
        return grabbed_cards

    def check_grab(self, pos, bot=False):
        """ Tries to grab a card in specified position.
        Returns True if card was just grabbed or there is already grabbed card that is not dropped yet.
        Otherwise returns False.
        :param pos: tuple with coordinates (x, y) - position of mouse click/screen touch.
        :param bot: if current player is a 'bot', i.e. virtual adversary (default False)
        :return: True if there is a card grabbed, False otherwise
        """
        if not self.grabbed_card and len(self.cards) > self.min_cards:
            if bot or self.cards[-1].check_mouse(pos, True):
                if self.cards[-1].back_up:
                    self.cards[-1].flip()
                self.grabbed_card = True
                return True
            else:
                return False
        else:
            return True

    def add_card(self, card_, on_top=True):
        """ Appends a card to the list of self.cards
        :param card_:  object of the Card class to be appended to the list
        :param on_top: bolean, True if the card should be put on top, False in the bottom
        """
        if isinstance(card_, card.Card):
            card_.unclick()
            if on_top:
                pos_ = self.pos
                if len(self.cards) is not 0:
                    l = len(self.cards)
                    pos_ = self.pos[0] + l * self.offset[0], self.pos[1] + l * self.offset[1]
                card_.set_pos(pos_)
                self.cards.append(card_)
            else:
                self.cards.insert(0, card_)
                self.update_position(self.offset)

    def pop_card(self, top):
        if len(self.cards) == 0:
            return None
        else:
            if len(self.cards) == 1 and self.last_card_callback is not None:
                self.last_card_callback(self.cards[0])
            if top:
                return self.cards.pop()
            else:
                return self.cards.pop(0)

    def pop_top_card(self):
        """ Removes top card from the list and returns it.
        If there are no cards left, returns None.
        """
        return self.pop_card(top=True)

    def pop_bottom_card(self):
        """ Removes last card from the list and returns it.
        If there are no cards left, returns None.
        """
        return self.pop_card(top=False)

    def drop_card(self):
        """ Drops grabbed card."""
        self.grabbed_card = False
        return self.pop_top_card()

    def flip_cards(self):
        """ Flip cards from face-up to face-down and vice versa """
        for card in self.cards:
            card.flip()

    def sort_cards(self):
        """ Sort cards by suits and ranks from lower to higher.
        Suits order: hearts, diamonds, clubs, spades.
        """
        self.cards.sort(key=operator.attrgetter('suit', 'rank'))

    def move_all_cards(self, other, back_side_up=True):
        """ Moves all cards to other cards holder.
        :param other: instance of AbstractCardsHolder where cards will be moved.
        :param back_side_up: boolean, True if cards should be flipped to back side up, False otherwise.
        """
        if isinstance(other, AbstractCardsHolder):
            while len(self.cards) != 0:
                card_ = self.pop_top_card()
                if card_ is not None:
                    if card_.back_up != back_side_up:
                        card_.flip()
                    other.add_card(card_)

    def update_position(self, offset):
        """ Updates position of all cards according to the offset passed
        :param offset: tuple (x, y) with values of offset for each card
        """
        pos_ = self.pos
        for card_ in self.cards:
            card_.set_pos(pos_)
            pos_ = pos_[0] + offset[0], pos_[1] + offset[1]

    def check_collide(self, card_):
        """ Checks if current cards holder collides with other card.
        :param card_: Card object to check collision with
        :return: True if card collides with holder, False otherwise
        """
        if len(self.cards) > 0:
            return self.cards[-1].check_collide(card_=card_)
        else:
            return card_.check_collide(pos=self.pos)

    def render(self, screen):
        pass
