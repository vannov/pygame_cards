#!/usr/bin/env python
try:
    import sys

    from pygame_cards import card_holder
    from pygame_cards import card_sprite, globals
except ImportError as err:
    print "Fail loading a module: %s", err
    sys.exit(2)


class Heap(card_holder.CardsHolder):
    """ Heap of cards on the table, active cards thrown by players
    """

    def __init__(self, pos):
        card_holder.CardsHolder.__init__(self)
        self.pos = pos

    def add_card(self, card_, player_name, move=True):
        if not move:
            card_.set_pos(self.calc_card_pos(player_name))
        self.cards.append(card_)

    def remove_card(self):
        return self.cards.pop(0)

    def calc_card_pos(self, player_name):
        card_x = self.pos[0]
        card_y = self.pos[1]
        l_offset = globals.settings_json["heap"]["offset"]
        if player_name is "north":
            card_y -= l_offset[1]
        elif player_name is "south":
            card_y += l_offset[1]
        elif player_name is "west":
            card_x -= l_offset[0]
        elif player_name is "east":
            card_x += l_offset[0]
        return card_x, card_y

