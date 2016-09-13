#!/usr/bin/env python
try:
    import sys

    import pidr_enums
    import logic
    from pygame_cards import globals, enums, card_sprite
    from pygame_cards import card_holder

except ImportError as err:
    print "Fail loading a module: %s", err
    sys.exit(2)


class Player(card_holder.CardsHolder):
    def __init__(self, name, pos, bot = True):
        card_holder.CardsHolder.__init__(self, 1)
        self.name = name
        self.pos = pos
        self.bot = bot
        self.talon = []
        self.move = None

    def add_card(self, card, type, move=True):
        if not move:
            card.set_pos(self.calc_card_pos(type))
        if type == pidr_enums.PidrCardType.talon:
            self.talon.append(card)
        elif type == pidr_enums.PidrCardType.open:
            if card.back_up:
                card.flip()
            self.cards.append(card)
        elif type == pidr_enums.PidrCardType.regular:
            if not card.back_up:
                card.flip()
            self.cards.append(card)

    def remove_card(self, card):
        self.cards.remove(card)
        if len(self.cards) == 0:
            if len(self.talon) != 0:
                for c in self.talon:
                    c.flip()
                    self.talon.remove(c)
                    self.cards.append(c)
            else:
                # todo: process win / check lap over
                pass
        self.reset_cards_pos()

    def calc_card_pos(self, type):
        offset = 0, 0
        l = len(self.cards)
        if type == pidr_enums.PidrCardType.talon:
            offset = globals.settings_json["player"]["player_talon_offset"]
            l = len(self.talon)
        p = self.pos[0] + offset[0] + l * globals.settings_json["player"]["player_card_offset_small"][0], \
            self.pos[1] + offset[1] + l * globals.settings_json["player"]["player_card_offset_small"][1]
        return p

    def reset_cards_pos(self):
        offset = 0, 0
        i = 0
        for card in self.cards:
            card.set_pos((self.pos[0] + offset[0] + i * globals.settings_json["player"]["player_card_offset_large"][0],
                         self.pos[1] + offset[1] + i * globals.settings_json["player"]["player_card_offset_large"][1]))
            i += 1

    def render(self, screen):
        for card in self.talon:
            card.render(screen)
        for card in self.cards:
            card.render(screen)
