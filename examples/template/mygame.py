import os
import pygame

from pygame_cards import game_app, controller, enums, globals, deck, abstract_card_holder, card


class MyGameController(controller.Controller):
    """ Main class that controls game logic and handles user events.
        Methods below are mandatory for all classes that derive from Controller.
        Do not use them directly, they are used by GameApp class. See comments in the main() method below.
        Other auxiliary methods can be added if needed and called from the mandatory methods. """

    def build_custom_objects(self):
        """
        """

        deck_pos = globals.settings_json["deck"]["position"]
        deck_offset = globals.settings_json["deck"]["offset"]
        self.deck = deck.Deck(type_=enums.DeckType.short, pos=deck_pos, offset=deck_offset)

        stack_pos = globals.settings_json["stack"]["position"]
        stack_offset = globals.settings_json["stack"]["offset"]
        self.stack = abstract_card_holder.AbstractCardsHolder(pos=stack_pos, offset=stack_offset)

        # All game objects should be added to self objects list with add_object method in order to be rendered.
        self.add_object((self.deck, self.stack))

        # Create Restart button
        self.gui_interface.show_button(globals.settings_json["gui"]["restart_button"], "Restart", self.restart_game)

    def start_game(self):
        """
        """

        # Shuffle cards in the deck
        self.deck.shuffle()

    def restart_game(self):
        """
        """

        self.stack.move_all_cards(self.deck)
        self.start_game()

    def execute_game(self):
        """
        """
        pass

    def process_mouse_event(self, pos, down, double_click):
        """
        """
        if down and self.deck.is_clicked(pos):
            card_ = self.deck.pop_top_card()
            if isinstance(card_, card.Card):
                card_.flip()
                self.stack.add_card(card_)

    def cleanup(self):
        """ Called when user closes the app. Should destroy all objects, store game progress to a file etc. """
        del self.deck
        del self.stack


def main():
    # JSON files contains game settings like window size, position of game and gui elements etc.
    json_path = os.path.join(os.getcwd(), 'settings.json')

    # Create an instance of GameApp and pass a path to setting json file and an instance of custom Controller object.
    # This will initialize the game, build_custom_objects() from Controller will be called at this step.
    solitaire_app = game_app.GameApp(json_path=json_path, game_controller=MyGameController())

    # Start executing the game. This will call start_game() from Controller,
    # then will be calling execute_game() in an endless loop.
    solitaire_app.execute()

if __name__ == '__main__':
    main()
