#!/usr/bin/env python
try:
    import sys
    from random import shuffle

    import pidr_enums
    from pygame_cards import globals
    from pygame_cards import enums
    import card
    import abstract_card_holder

except ImportError as err:
    print "Fail loading a module: %s", err
    sys.exit(2)


class Deck(abstract_card_holder.AbstractCardsHolder):
    """ Deck of cards. Two types of deck available: short (6..ace) and full (2..ace)"""

    def __init__(self, type_, pos, last_card_callback=None):
        """
        :param type_: int value that corresponds to enum from enums.DeckType class
        :param pos: tuple with coordinates (x, y) for bottom card in the desk
        :param last_card_callback: function that should be called when the last card is removed from the deck
        """
        abstract_card_holder.AbstractCardsHolder.__init__(self, 0, last_card_callback)
        self.pos = pos
        self.type = type_

        start = 0
        if type_ == enums.DeckType.short:
            start = enums.Rank.six
        elif type_ == enums.DeckType.full:
            start = enums.Rank.two
        else:
            assert "Deck type invalid"  # TODO: remove?

        card_pos = pos
        for r in range(start, enums.Rank.ace + 1):
            for s in range(enums.Suit.hearts, enums.Suit.spades):
                self.cards.append(card.Card(s, r, card_pos, True))

    def shuffle(self):
        """ Shuffles cards in the deck randomly """
        shuffle(self.cards)
        offset = 0, 0
        for card_ in self.cards:
            card_.offset_pos(offset)
            offset = offset[0] + \
                     globals.settings_json["deck"]["offset"][0], offset[1] + globals.settings_json["deck"]["offset"][1]

    def render(self, screen):
        """ Renders all cards from the deck on a screen passed in argument
        :param screen: screen to render the card's sprite on
        """
        for card_ in self.cards:
            card_.render(screen)
