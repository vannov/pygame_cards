try:
    import sys
    import pygame

    from pygame_cards import card_holder, enums, card
except ImportError as err:
    print("Fail loading a module in file:", __file__, "\n", err)
    sys.exit(2)


def draw_empty_card_pocket(holder, screen):
    """ Renders empty card pocket at the position of CardHolder object
    :param holder: CardsHolder object
    :param screen: Screen object to render onto
    """
    if len(holder.cards) == 0:
        rect = (holder.pos[0], holder.pos[1],
                card_holder.CardsHolder.card_json["size"][0],
                card_holder.CardsHolder.card_json["size"][1])
        pygame.draw.rect(screen, (77, 77, 77), rect, 2)


class Foundation(card_holder.CardsHolder):
    def can_drop_card(self, card_):
        """ Check if a card can be dropped into a foundation. Conditions:
        - If a pocket is empty, only an ace can be dropped
        - If a pocket is not empty, only a card of the same suit and lower by 1 rank can be dropped
        :param card_: Card object to be dropped
        :return: Boolean, True if a card can be dropped, False otherwise
        """
        if len(self.cards) == 0:
            return card_.rank == enums.Rank.ace
        elif len(self.cards) == 1:
            return self.cards[-1].suit == card_.suit and card_.rank == enums.Rank.two
        else:
            return self.cards[-1].suit == card_.suit and card_.rank - self.cards[-1].rank == 1

    def render(self, screen):
        draw_empty_card_pocket(self, screen)


class Pile(card_holder.CardsHolder):
    def can_drop_card(self, card_):
        """ Check if a card can be dropped into a pile. Conditions:
        - If a pile is empty, only a King can be dropped
        - If a pile is not empty, only a card with opposite suit color and lower by 1 rank can
        be dropped
        :param card_: Card object to be dropped
        :return: Boolean, True if a card can be dropped, False otherwise
        """
        if len(self.cards) == 0:
            return card_.rank == enums.Rank.king
        elif self.cards[-1].rank == enums.Rank.ace:
            return False
        else:
            return self.cards[-1].rank - card_.rank == 1 and\
                ((card_.suit in [enums.Suit.hearts, enums.Suit.diamonds] and
                  self.cards[-1].suit in [enums.Suit.clubs, enums.Suit.spades]) or
                 (card_.suit in [enums.Suit.clubs, enums.Suit.spades] and
                  self.cards[-1].suit in [enums.Suit.hearts, enums.Suit.diamonds]))

    def open_top_card(self):
        """ Flips top card face up. """
        if len(self.cards) > 0 and self.cards[-1].back_up:
            self.cards[-1].flip()

    def render(self, screen):
        draw_empty_card_pocket(self, screen)


class GrabbedCardsHolder(card_holder.CardsHolder):
    """Holds cards currently grabbed by the user (ie under the mouse with the button held down)"""
    def add_card(self, card_, on_top=False):
        if isinstance(card_, card.Card):
            if on_top:
                self.cards.append(card_)
            else:
                self.cards.insert(0, card_)

    def render(self, screen):
        if len(self.cards) > 0:
            self.pos = self.cards[0].get_sprite().pos
            self.update_position(self.offset)
            _ = screen


class DeckDiscard(card_holder.CardsHolder):
    """ Container for temporary discarded cards from Decks. Invisible object, nothing renders.
        When Deck scrolling cycle is over, cards from this holder will move back to Deck.
    """

    def render_all(self, screen):
        """ Override this method from GameObject class in order to not render any cards.
        :param screen: Screen to render objects on
        """
        pass
