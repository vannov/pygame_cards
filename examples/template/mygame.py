import os

# Import other modules from pygame_cards if needed.
from pygame_cards import game_app, controller  # , enums, card_holder, deck, card


class MyGameController(controller.Controller):
    """ Main class that controls game logic and handles user events.

        Following methods are mandatory for all classes that derive from Controller:
            - build_objects()
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

    def build_objects(self):
        """ Create permanent game objects (deck of cards, players etc.) and GUI elements
            in this method. This method is executed during creation of GameApp object.
        """
        pass

    def start_game(self):
        """ Put game initialization code here. For example: dealing of cards,
            initialization of game timer etc. This method is triggered by GameApp.execute().
        """
        pass

    def process_mouse_event(self, pos, down, double_click):
        """ Put code that handles mouse events here. For example: grab card from a deck
            on mouse down event, drop card to a pile on mouse up event etc.
            This method is called every time mouse event is detected.
            :param pos: tuple with mouse coordinates (x, y)
            :param down: boolean, True for mouse down event, False for mouse up event
            :param double_click: boolean, True if it's a double click event
        """
        pass

    def restart_game(self):
        """ Put code that cleans up any current game progress and starts the game from scratch.
            start_game() method can be called here to avoid code duplication. For example,
            This method can be used after game over or as a handler of "Restart" button.
        """
        pass

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
        pass


def main():
    """ Entry point of the application. """

    # JSON files contains game settings like window size, position of game and gui elements etc.
    # Necessary fields are "window", "card" and "gui" - they are added to settings.json
    # in this example. Feel free to add any custom fields to that file, they will be accessible
    # via "self.settings_json" attribute of your class derived from controller.Controller.
    # See how custom fields from JSON are used in mygame_examples.py
    json_path = os.path.join(os.getcwd(), 'settings.json')

    # Create an instance of GameApp and pass a path to setting json file
    # and an instance of custom Controller object.
    # This will initialize the game, build_objects() from Controller will be called at this step.
    solitaire_app = game_app.GameApp(json_path=json_path, game_controller=MyGameController())

    # Start executing the game. This will call start_game() from Controller,
    # then will be calling execute_game() in an endless loop.
    solitaire_app.execute()

if __name__ == '__main__':
    main()
