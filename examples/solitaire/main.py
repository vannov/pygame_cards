#!/usr/bin/env python
try:
    import sys
    import os
    import pygame

    from pygame_cards import game_app, controller, deck, abstract_card_holder, enums, globals, card
except ImportError as err:
    print "Fail loading a module: %s", err
    sys.exit(2)


def draw_empty_card_pocket(screen, pos):
    rect = (pos[0], pos[1], globals.settings_json["card"]["size"][0], globals.settings_json["card"]["size"][1])
    pygame.draw.rect(screen, (77, 77, 77), rect, 2)


class Foundation(abstract_card_holder.AbstractCardsHolder):
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
            return self.cards[-1].suit == card_.suit and self.cards[-1].rank - card_.rank == 1

    def pop_top_card(self):
        """ Overwrite pop_top_card() method of AbstractCardsHolder to restrict taking cards from a foundation.
        :return: None
        """
        return None

    def render(self, screen):
        if len(self.cards) == 0:
            draw_empty_card_pocket(screen, self.pos)


class Pile(abstract_card_holder.AbstractCardsHolder):
    def can_drop_card(self, card_):
        """ Check if a card can be dropped into a foundation. Conditions:
            - If a pile is empty, only a King ca be dropped
            - If a pile is not empty, only a card with opposite suit color and lower by 1 rank can be dropped
        :param card_: Card object to be dropped
        :return: Boolean, True if a card can be dropped, False otherwise
        """
        if len(self.cards) == 0:
            return card_.rank == enums.Rank.king
        else:
            return self.cards[-1].rank - card_.rank == 1 and\
                ((card_.suit in [enums.Suit.hearts, enums.Suit.diamonds] and
                  self.cards[-1].suit in [enums.Suit.clubs, enums.Suit.spades]) or
                 (card_.suit in [enums.Suit.clubs, enums.Suit.spades] and
                  self.cards[-1].suit in [enums.Suit.hearts, enums.Suit.diamonds]))

    def open_top_card(self):
        if len(self.cards) > 0 and self.cards[-1].back_up:
            self.cards[-1].flip()

    def render(self, screen):
        if len(self.cards) == 0:
            draw_empty_card_pocket(screen, self.pos)


class GrabbedCardsHolder(abstract_card_holder.AbstractCardsHolder):
    def add_card(self, card_, on_top=False):
        if isinstance(card_, card.Card):
            if len(self.cards) == 0:
                self.pos = card_.get_sprite().pos
            if on_top:
                self.cards.append(card_)
            else:
                self.cards.insert(0, card_)
            self.update_position(self.offset)

    def render(self, screen):
        self.update_position(self.offset)


class SolitaireController(controller.Controller):

    def start_game(self):
        self.deck.shuffle()
        #self.deal_cards()

        pile_pos = globals.settings_json["pile"]["position"]
        pile_offset = globals.settings_json["pile"]["offset"]
        pile_inner_offset = globals.settings_json["pile"]["inner_offset"]
        for i in range(1, 8):
            pile = Pile(pile_pos, pile_inner_offset, enums.GrabPolicy.can_multi_grab)
            for j in range(0, i):
                card_ = self.deck.pop_top_card()
                if j == i - 1:
                    card_.flip()
                pile.add_card(card_)
            self.add_object(pile)
            self.piles.append(pile)
            pile_pos = pile_pos[0] + pile_offset[0], pile_pos[1] + pile_offset[1]

        self.grabbed_cards_holder = GrabbedCardsHolder((0, 0), pile_inner_offset)
        self.add_object(self.grabbed_cards_holder)
        self.owner_of_grabbed_card = None

    def build_custom_objects(self):
        deck_pos = globals.settings_json["deck"]["position"]
        deck_offset = globals.settings_json["deck"]["offset"]
        # TODO create callback
        self.deck = deck.Deck(enums.DeckType.full, deck_pos, deck_offset, None)

        deck_pos = self.deck.pos
        x_offset = globals.settings_json["stack"]["deck_offset"][0] + globals.settings_json["card"]["size"][0]
        y_offset = globals.settings_json["stack"]["deck_offset"][1]
        stack_pos = deck_pos[0] + x_offset, deck_pos[1] + y_offset
        stack_offset = globals.settings_json["stack"]["inner_offset"]
        self.stack = abstract_card_holder.AbstractCardsHolder(stack_pos, stack_offset, enums.GrabPolicy.can_single_grab)

        foundation_pos = globals.settings_json["foundation"]["position"]
        foundation_offset = globals.settings_json["foundation"]["offset"]
        foundation_inner_offset = globals.settings_json["foundation"]["inner_offset"]
        self.foundations = []
        for i in range(0, 4):
            self.foundations.append(Foundation(foundation_pos, foundation_inner_offset))
            foundation_pos = foundation_pos[0] + foundation_offset[0], foundation_pos[1] + foundation_offset[1]
            self.add_object(self.foundations[i])

        self.add_object((self.deck, self.stack))
        self.piles = []

    def execute_game(self):
        pass

    def process_mouse_event(self, pos, down):
        if down:
            self.process_mouse_down(pos)
        else:
            self.process_mouse_up(pos)

    def process_mouse_down(self, pos):
        if self.deck.is_clicked(pos):
            self.process_deck_click()
            return

        if len(self.grabbed_cards_holder.cards) == 0:
            for obj in self.objects:
                grabbed_cards = obj.try_grab_card(pos)
                if grabbed_cards is not None:
                    for c in grabbed_cards:
                        self.grabbed_cards_holder.add_card(c)
                    self.owner_of_grabbed_card = obj
                    break

    def process_mouse_up(self, pos):
        if len(self.grabbed_cards_holder.cards) > 0:
            for obj in self.objects:
                dropped_cards = False
                if hasattr(obj, "can_drop_card") and obj.is_clicked(pos) and \
                        obj.can_drop_card(self.grabbed_cards_holder.cards[0]):
                    dropped_cards = True
                    while len(self.grabbed_cards_holder.cards) != 0:
                        obj.add_card(self.grabbed_cards_holder.pop_top_card())
                    break
            if self.owner_of_grabbed_card is not None:
                while len(self.grabbed_cards_holder.cards) != 0:
                    self.owner_of_grabbed_card.add_card(self.grabbed_cards_holder.pop_top_card())
                if dropped_cards and isinstance(self.owner_of_grabbed_card, Pile):
                    self.owner_of_grabbed_card.open_top_card()
                self.owner_of_grabbed_card = None

    def process_deck_click(self):
        while len(self.stack.cards) != 0:
            card_ = self.stack.pop_top_card()
            if card_ is not None:
                card_.flip()
                self.deck.add_card(card_, on_top=False)

        for i in range(0, 3):
            card_ = self.deck.pop_top_card()
            if card_ is None:
                break
            card_.flip()
            self.stack.add_card(card_)


class SolitaireApp(game_app.GameApp):
    """ Class the represents Solitaire application """

    def load_game_settings_from_json(self):
        pass

    def build_game_controller(self):
        return SolitaireController()


def main():
    json_path = os.path.join(os.getcwd(), 'settings.json')
    solitaire_app = SolitaireApp(json_path)
    solitaire_app.execute()

if __name__ == '__main__':
    main()
