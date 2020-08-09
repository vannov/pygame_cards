#!/usr/bin/env python
try:
    import sys
    import operator
    import pygame

    from pygame_cards import game_object, card, enums
except ImportError as err:
    print("Fail loading a module in file:", __file__, "\n", err)
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

    def is_clicked(self, pos):
        """ Checks if any part of the holder is clicked, even if it has no cards.
        :param pos: tuple with coordinates (x, y) - position of mouse click/screen touch.
        :return: True if holder is clicked, False otherwise
        """
        if len(self.cards) is not 0:
            # Check if any card clicked.
            return any(card_.is_clicked(pos) for card_ in self.cards)
        else:
            # No cards, but check if the holder's empty area clicked.
            return \
                pos[0] > self.pos[0]\
                and pos[0] < (self.pos[0] + CardsHolder.card_json["size"][0])\
                and pos[1] > self.pos[1]\
                and pos[1] < (self.pos[1] + CardsHolder.card_json["size"][1])

    def is_top_card_clicked(self, pos):
        """ Checks if a top card is clicked.
        :param pos: tuple with coordinates (x, y) - position of mouse click/screen touch.
        :return: True if top card is clicked, False otherwise
        """
        return len(self.cards) is not 0 and self.cards[-1].is_clicked(pos)

    def try_grab_card_at(self, pos):
        """ Tries to grab a card (or multiple cards) at given screen position.
        :param pos: tuple with coordinates (x, y) - position of mouse click/screen touch.
        :return: Tuple of:
                 - List with Card object if grabbed or None if card can't be grabbed or mouse click
                   is not on the holder.
                 - Offset between given pos and pos of grabbed card.
        """
        (card_, grab_offset) = self.card_at(pos)
        return (self.try_grab_card(card_), grab_offset)

    def try_grab_card(self, card_):
        """ Tries to grab a card (or multiple cards).
        :param card_: Given card at which to grab.
        :return: List with Card object if grabbed or None if card can't be grabbed.
        """
        grabbed_cards = None

        if card_ is not None and self.can_grab_card(card_):
            index = self.cards.index(card_)

            if self.grab_policy == enums.GrabPolicy.can_multi_grab:
                if index == 0 and self.last_card_callback is not None:
                    self.last_card_callback(self.cards[0])
                grabbed_cards = [c for c in self.cards if self.cards.index(c) >= index]
                self.cards[:] = [c for c in self.cards if self.cards.index(c) < index]
            else:
                grabbed_cards = [self.pop_card(index)]

        return grabbed_cards

    def can_grab_card(self, card_):
        """Determine if a given card from the holder can be grabbed
        out of the holder.
        :param card_: Card that is expected to be in the current holder.
        """
        if self.grab_policy == enums.GrabPolicy.no_grab:
            return False
        elif len(self.cards) == 0:
            return False
        elif self.grab_policy == enums.GrabPolicy.can_single_grab:
            return card_ is self.cards[-1]
        else:
            return card_ in self.cards

    def card_at(self, pos):
        """See which card is at a given position.
        :param pos: tuple with coordinates (x, y) - position on screen.
        :return: tuple of card being touched (or None),
            mouse offset of card position from given position (or None)
        """
        for card_ in reversed(self.cards):
            if card_.is_clicked(pos):
                card_pos = card_.get_pos()
                return (\
                    card_,\
                    (pos[0] - card_pos[0], pos[1] - card_pos[1]))

        return (None, None)

    def add_card(self, card_, on_top=True):
        """ Appends a card to the list of self.cards
        :param card_:  object of the Card class to be appended to the list
        :param on_top: bolean, True if the card should be put on top, False in the bottom
        """
        if isinstance(card_, card.Card):
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

    def pop_card(self, index):
        """ Removes top or bottom cards from the list and returns it.
        :param index: Index of card to remove.
        :return: Card object
        """
        if len(self.cards) == 0:
            return None
        else:
            if len(self.cards) == 1 and self.last_card_callback is not None:
                self.last_card_callback(self.cards[0])

            popped_card = self.cards.pop(index)
            self.update_position(self.offset)
            return popped_card

    def pop_top_card(self):
        """ Removes top card from the list and returns it.
        If there are no cards left, returns None.
        :return: Card object
        """
        return self.pop_card(-1)

    def pop_bottom_card(self):
        """ Removes last card from the list and returns it.
        If there are no cards left, returns None.
        :return: Card object
        """
        return self.pop_card(0)

    def flip_cards(self):
        """ Flip cards from face-up to face-down and vice versa """
        for card_ in self.cards:
            card_.flip()

    def sort_cards(self, key_func=operator.attrgetter('suit', 'rank')):
        """ Sort cards by the given key function.
        :param key_func: Key function for sorting cards. By default,
            suits and ranks from lower to higher.
            Suits order: hearts, diamonds, clubs, spades.
        """
        self.cards.sort(key=key_func)
        self.update_position(self.offset)

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
            if self.grab_policy == enums.GrabPolicy.can_single_grab:
                # If can only grab top card, then only check for collision
                # with top card.
                return self.cards[-1].check_collide(card_=card_)
            else:
                # Any other grab policy, check all cards for collision.
                return any(c.check_collide(card_=card_) for c in reversed(self.cards))
        else:
            return card_.check_collide(pos=self.pos)

    def render(self, screen):
        """ Does not render anything by default.
        Should be overridden in derived classes if need to render anything for the holder itself.
        Cards in the holder are rendered by higher level render_all().
        :param screen: Screen to render objects on
        """
        pass


class GrabbedCardsHolder(CardsHolder):
    """Specialized card holder, where the position always follows the mouse.
    """
    def __init__(self, mouse_offset=(0, 0), offset=(0, 0),
                 grab_policy=enums.GrabPolicy.no_grab,
                 last_card_callback=None):
        """
        :param offset: tuple (x, y) with values of offset between cards in the holder
        :param grab_policy: value from enums.GrabPolicy (by default enums.GrabPolicy.no_grab)
        :param last_card_callback: function to be called once the last card removed (default None)
        """
        self.mouse_offset = mouse_offset
        CardsHolder.__init__(self, self.get_target_pos(), offset, grab_policy,\
            last_card_callback)


    def render_all(self, screen):
        # Track the mouse position.
        self.pos = self.get_target_pos()
        self.update_position(self.offset)

        super().render_all(screen)


    def get_target_pos(self):
        """Get the current desired position of this holder, whose purpose
        is to track the position of the mouse.
        """
        mouse_pos = pygame.mouse.get_pos()
        return (\
            mouse_pos[0] - self.mouse_offset[0],\
            mouse_pos[1] - self.mouse_offset[1])
