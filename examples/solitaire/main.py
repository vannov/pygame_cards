#!/usr/bin/env python
try:
    import sys
    import os
    import imp
    import pygame

    import pygame_cards
    from pygame_cards import game_app
except ImportError as err:
    print "Fail loading a module: %s", err
    sys.exit(2)


class SolitaireApp(game_app.GameApp):
    """ Class the represents Solitaire application """

    def load_game_settings_from_json(self):
        pass

    def process_mouse_event(self, down):
        pass

    def build_game_objects(self):
        pass


def main():
    json_path = os.path.join(os.getcwd(), 'settings.json')
    solitaire_app = SolitaireApp(json_path)
    solitaire_app.execute()

if __name__ == '__main__':
    main()
