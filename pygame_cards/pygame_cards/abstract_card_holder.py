#!/usr/bin/env python
try:
    import sys
    import abc
    import operator
    from random import shuffle

except ImportError as err:
    print "Fail loading a module: %s", err
    sys.exit(2)


class AbstractCardsHolder:
    """ Abstract card holder, from which a card can be grabbed and moved to a different cards holder.
    Ex.: a player (player's pile of cards), a deck of cards.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, min_cards=0, last_card_callback=None):
        """
        :param min_cards: minimum number of cards required for cards holder to exist (default 0)
        :param last_card_callback: function to be called once the last card is removed (default None)
        """
        self.cards = []
        self.grabbed_card = False
        self.min_cards = min_cards
        self.last_card_callback = last_card_callback

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

    def pop_top_card(self):
        """ Removes top card from the list and returns it.
        If there are no cards left, returns None.
        """
        if len(self.cards) == 0:
            return None
        else:
            if len(self.cards) == 1 and self.last_card_callback is not None:
                self.last_card_callback(self.cards[0])
            return self.cards.pop()

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

    #@abc.abstractmethod
    def render(self, screen):
        """ Renders cards' sprites """
        for card in self.cards:
            card.render(screen)
