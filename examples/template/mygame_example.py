import os

# Import other modules from pygame_cards if needed.
from pygame_cards import game_app, controller, enums, card_holder, deck, card


class MyGameController(controller.Controller):
    """ Main class that controls game logic and handles user events.

        Following methods are mandatory for all classes that derive from Controller:
            - start_game()
            - process_mouse_events()

        Also these methods are not mandatory, but it can be helpful to define them:
            - execute_game()
            - restart_game()
            - cleanup()

        These methods are called from higher level GameApp class.
        See details about each method below.
        Other auxiliary methods can be added if needed and called from the mandatory methods.
    """

    def __init__(self, objects_list=None, gui_interface=None, settings_json=None):
        super(MyGameController, self).__init__(objects_list=objects_list, gui_interface=gui_interface, settings_json=settings_json)

        deck_pos = self.settings_json["deck"]["position"]
        deck_offset = self.settings_json["deck"]["offset"]
        self.deck = deck.Deck(type_=enums.DeckType.short, pos=deck_pos, offset=deck_offset)

        stack_pos = self.settings_json["stack"]["position"]
        stack_offset = self.settings_json["stack"]["offset"]
        self.stack = card_holder.CardsHolder(pos=stack_pos, offset=stack_offset)

        # All game objects should be added to self objects list
        #  with add_object method in order to be rendered.
        self.add_rendered_object((self.deck, self.stack))

        # Create Restart button
        self.gui_interface.show_button(self.settings_json["gui"]["restart_button"],
                                       self.restart_game, "Restart")

    def start_game(self):
        """ Put game initialization code here.
            For example: dealing of cards, initialization of game timer etc.
            This method is triggered by GameApp.execute().
        """

        # Shuffle cards in the deck
        self.deck.shuffle()

    def process_mouse_event(self, pos, down, double_click):
        """ Put code that handles mouse events here.
            For example: grab card from a deck on mouse down event,
            drop card to a pile on mouse up event etc.
            This method is called every time mouse event is detected.
            :param pos: tuple with mouse coordinates (x, y)
            :param down: boolean, True for mouse down event, False for mouse up event
            :param double_click: boolean, True if it's a double click event
        """
        if down and self.deck.is_clicked(pos):
            card_ = self.deck.pop_top_card()
            if isinstance(card_, card.Card):
                card_.flip()
                self.stack.add_card(card_)

    def restart_game(self):
        """ Put code that cleans up any current game progress and starts the game from scratch.
            start_game() method can be called here to avoid code duplication. For example,
            This method can be used after game over or as a handler of "Restart" button.
        """
        self.stack.move_all_cards(self.deck)
        self.start_game()

    def execute_game(self):
        """ This method is called in an endless loop started by GameApp.execute().
        IMPORTANT: do not put any "heavy" computations in this method!
        It is executed frequently in an endless loop during the app runtime,
        so any "heavy" code will slow down the performance.
        If you don't need to check something at every moment of the game, do not define this method.

        Possible things to do in this method:
             - Check game state conditions (game over, win etc.)
             - Run bot (virtual player) actions
             - Check timers etc.
        """
        pass

    def cleanup(self):
        """ Called when user closes the app.
            Add destruction of all objects, storing of game progress to a file etc. to this method.
        """
        del self.deck
        del self.stack


def main():
    """ Entry point of the application. """

    # JSON files contains game settings like window size, position of game and gui elements etc.
    json_path = os.path.join(os.getcwd(), 'settings_example.json')

    # Create an instance of GameApp and pass a path to setting json file
    # and a subclass of Controller. This will initialize the game,
    # and instantiate the Controller.
    solitaire_app = game_app.GameApp(json_path=json_path, controller_cls=MyGameController)

    # Start executing the game. This will call start_game() from Controller,
    # then will be calling execute_game() in an endless loop.
    solitaire_app.execute()

if __name__ == '__main__':
    main()
