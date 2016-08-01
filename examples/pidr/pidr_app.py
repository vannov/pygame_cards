#!/usr/bin/env python
try:
    import sys
    import os
    import pygame

    from pygame_cards import game_app, gui, enums
    from pygame_cards import globals, gui, enums, game_app
    from pygame_cards import deck
    import player, game_controller
except ImportError as err:
    print "Fail loading a module: %s", err
    sys.exit(2)


class PidrApp(game_app.GameApp):
    """ Main game controller class """

    def load_game_settings_from_json(self):
        self.deck_pos = (self.size[0] - globals.settings_json["card"]["size"][0])/2, (self.size[1] - globals.settings_json["card"]["size"][1])/2
        self.players_pos = {
            'west': (globals.settings_json["player"]["player_window_margin"], (self.size[1] - globals.settings_json["card"]["size"][1])/2),
            'north': ((self.size[0] - globals.settings_json["card"]["size"][0])/2, globals.settings_json["player"]["player_window_margin"]),
            'east': (self.size[0] - globals.settings_json["player"]["player_window_margin"] - globals.settings_json["card"]["size"][0], (self.size[1] - globals.settings_json["card"]["size"][1])/2),
            'south': ((self.size[0] - globals.settings_json["card"]["size"][0])/2, self.size[1] - globals.settings_json["player"]["player_window_margin"] - globals.settings_json["card"]["size"][1])
        }

    def build_game_objects(self):
        #deck = self.factory.create_deck(enums.DeckType.short, self.deck_pos)
        l_deck = deck.Deck(enums.DeckType.short, self.deck_pos, self.deck_last_card_callback)
        players = []
        players.append(player.Player('west', self.players_pos['west'], True))
        players.append(player.Player('north', self.players_pos['north'], True))
        players.append(player.Player('east', self.players_pos['east'], True))
        players.append(player.Player('south', self.players_pos['south'], False))
        self.game_controller = game_controller.PidrGameController(players, l_deck, self.gui_interface)

    def process_mouse_event(self, down):
        if self.gui_interface is not None:
            self.gui_interface.check_mouse(down)
        if self.game_controller is not None:
            self.game_controller.process_mouse_event(pygame.mouse.get_pos(), down)
        # for sprite in self.all_sprites_list:
        #     sprite.check_mouse(pygame.mouse.get_pos(), down)

    def deck_last_card_callback(self, card):
        self.game_controller.deck_last_card_callback(card)


def main():
    json_path = os.path.join(os.getcwd(), 'settings.json')
    print json_path
    pidr = PidrApp(json_path)
    pidr.execute()

if __name__ == '__main__':
    main()
