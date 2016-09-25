#!/usr/bin/env python
try:
    import sys
    import operator

    from pygame_cards import game_object, card, enums
except ImportError as err:
    print "Fail loading a module in file:", __file__, "\n", err
    sys.exit(2)


class CardsHolder(game_object.GameObject):
    """ Card holder, to which cards can be added and from which cards can be grabbed and moved
    to other cards holders. Ex.: a deck of cards, a player's pile of cards.
    Can be inherited and modified/extended for specific needs.

    Attributes:
        card_json - The 'card' node of the settings.json. Data can be accessed via [] operator,
                    for example: CardsHolder.card_json["size"][0]
    """

    card_json = None

    def __init__(self, pos=(0, 0), offset=(0, 0), grab_policy=enums.GrabPolicy.no_grab,
                 last_card_callback=None):
        """
        :param pos: tuple with coordinates (x, y) - position of top left corner of cards holder
        :param offset: tuple (x, y) with values of offset between cards in the holder
        :param grab_policy: value from enums.GrabPolicy (by default enums.GrabPolicy.no_grab)
        :param last_card_callback: function to be called once the last card removed (default None)
        """
        self.cards = []
        game_object.GameObject.__init__(self, self.cards, grab_policy)
        self.last_card_callback = last_card_callback
        self.pos = pos
        self.offset = offset
        self.grabbed_card = None

    def is_clicked(self, pos):
        """ Checks if a top card is clicked.
        :param pos: tuple with coordinates (x, y) - position of mouse click/screen touch.
        :return: True if top card is clicked, False otherwise
        """
        if len(self.cards) is not 0:
            if self.cards[-1].is_clicked(pos):
                return True
        elif pos[0] > self.pos[0] and pos[0] < (self.pos[0] + CardsHolder.card_json["size"][0]) and\
             pos[1] > self.pos[1] and pos[1] < (self.pos[1] + CardsHolder.card_json["size"][1]):
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
        :return: List with Card object if grabbed or None if card can't be grabbed or mouse click
                 is not on the holder.
        """
        grabbed_cards = None
        if len(self.cards) > 0:
            if self.grab_policy == enums.GrabPolicy.can_single_grab:
                if self.check_click(pos):
                    grabbed_cards = [self.pop_top_card()]
            elif self.grab_policy == enums.GrabPolicy.can_multi_grab:
                index = -1
                for card_ in reversed(self.cards):
                    if card_.back_up:
                        break
                    if card_.check_mouse(pos, True):
                        index = self.cards.index(card_)
                        break

                if index != -1:
                    grabbed_cards = [c for c in self.cards if self.cards.index(c) >= index]
                    grabbed_cards.reverse()
                    self.cards[:] = [c for c in self.cards if self.cards.index(c) < index]
        return grabbed_cards

    def check_grab(self, pos, bot=False):
        """ Tries to grab a card in specified position.
        Returns True if card was grabbed or there is already grabbed card that is not dropped yet.
        Otherwise returns False.
        :param pos: tuple with coordinates (x, y) - position of mouse click/screen touch.
        :param bot: if current player is a 'bot', i.e. virtual adversary (default False)
        :return: True if there is a card grabbed, False otherwise
        """
        if not self.grabbed_card and len(self.cards) > 0:
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
                    length = len(self.cards)
                    pos_ = (self.pos[0] + length * self.offset[0],
                            self.pos[1] + length * self.offset[1])
                card_.set_pos(pos_)
                self.cards.append(card_)
            else:
                self.cards.insert(0, card_)
                self.update_position(self.offset)

    def pop_card(self, top):
        """ Removes top or bottom cards from the list and returns it.
        :param top: boolean, if True top card is removed, otherwise bottom card is removed.
        :return: Card object
        """
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
        :return: Card object
        """
        return self.pop_card(top=True)

    def pop_bottom_card(self):
        """ Removes last card from the list and returns it.
        If there are no cards left, returns None.
        :return: Card object
        """
        return self.pop_card(top=False)

    def drop_card(self):
        """ Drops grabbed card."""
        self.grabbed_card = False
        return self.pop_top_card()

    def flip_cards(self):
        """ Flip cards from face-up to face-down and vice versa """
        for card_ in self.cards:
            card_.flip()

    def sort_cards(self):
        """ Sort cards by suits and ranks from lower to higher.
        Suits order: hearts, diamonds, clubs, spades.
        """
        self.cards.sort(key=operator.attrgetter('suit', 'rank'))

    def move_all_cards(self, other, back_side_up=True):
        """ Moves all cards to other cards holder.
        :param other: instance of CardsHolder where cards will be moved.
        :param back_side_up: True if cards should be flipped to back side up, False otherwise.
        """
        if isinstance(other, CardsHolder):
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
        """ Does not render anything by default.
        Should be overridden in derived classes if need to render anything for the holder itself.
        Cards in the holder are rendered by higher level render_all().
        :param screen: Screen to render objects on
        """
        pass
