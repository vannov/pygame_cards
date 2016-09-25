#!/usr/bin/env python
try:
    import sys
    import abc

    from pygame_cards import game_object, card, card_sprite
except ImportError as err:
    print "Fail loading a module in file:", __file__, "\n", err
    sys.exit(2)


class Controller(object):
    """ Abstract interface class that controls game logic and handles user events,
        Should be inherited by concrete game controller classes.

        Following methods are mandatory for all classes that derive from Controller:
            - build_objects()
            - start_game()
            - process_mouse_events()

        Also these methods are not mandatory, but it can be helpful to define them:
            - execute_game()
            - restart_game()
            - cleanup()

        These methods are called from high level GameApp class. See details about each method below.
        Other auxiliary methods can be added if needed and called from the mandatory methods.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, objects_list=None, gui_interface=None, settings_json=None):
        """
        Initializes Controller object.
        :param objects_list: list of game objects that should be rendered
        :param gui_interface: gui interface object
        """
        self.rendered_objects = []
        self.moves = []
        if objects_list is not None and isinstance(objects_list, list):
            self.rendered_objects = objects_list
        self.gui_interface = gui_interface
        self.settings_json = settings_json
        self.started = False

        # Dictionary where any custom objects needed can be stored
        self.custom_dict = dict()

    @abc.abstractmethod
    def build_objects(self):
        """ Create permanent game objects (deck of cards, players etc.) and GUI elements
            in this method. This method is executed during creation of GameApp object.
        """
        pass

    @abc.abstractmethod
    def start_game(self):
        """ Put game initialization code here.
            For example: dealing of cards, initialization of game timer etc.
            This method is triggered by GameApp.execute().
        """
        pass

    @abc.abstractmethod
    def process_mouse_event(self, pos, down, double_click):
        """ Put code that handles mouse events here. For example: grab card from a deck on mouse
            down event, drop card to a pile on mouse up event etc.
            This method is called every time mouse event is detected.
            :param pos: tuple with mouse coordinates (x, y)
            :param down: boolean, True for mouse down event, False for mouse up event
            :param double_click: boolean, True if it's a double click event
        """
        pass

    def execute_game(self):
        """ This method is called in an endless loop started by GameApp.execute().
        IMPORTANT: do not put any "heavy" computations in this method! It is executed frequently in
        an endless loop during the app runtime, so any "heavy" code will slow down the performance.
        If you don't need to check something at every moment of the game, do not define this method.

        Possible things to do in this method:
             - Check game state conditions (game over, win etc.)
             - Run bot (virtual player) actions
             - Check timers etc.
        """
        pass

    def restart_game(self):
        """ Put code that cleans up any current game progress and starts the game from scratch.
            start_game() method can be called here to avoid code duplication.
            For example this method can be used after game over or as a handler of "Restart" button.
        """
        pass

    def cleanup(self):
        """ Called when user closes the app.
            Add destruction of all objects, storing of game progress to a file etc. to this method.
        """
        pass

    def render_objects(self, screen):
        """ Renders game objects.
        :param screen: Screen to render objects on.
        """
        if self.rendered_objects is not None:
            for obj in self.rendered_objects:
                if isinstance(obj, game_object.GameObject):
                    obj.render_all(screen)

        if len(self.moves) > 0:
            self.moves[0].update()
            if self.moves[0].is_completed():
                self.moves.pop(0)

    def add_rendered_object(self, obj):
        """ Adds object to the list of objects to be rendered by the Controller.
        :param obj: an instance of GameObject or derived class.
        """
        if self.rendered_objects is None:
            self.rendered_objects = []
        if isinstance(obj, tuple):
            self.rendered_objects.extend(obj)
        elif isinstance(obj, game_object.GameObject):
            self.rendered_objects.append(obj)

    def remove_rendered_object(self, id_):
        """ Removes an object from the list of rendered_objects by id
        :param id_: string with unique object id
        """
        # TODO: implement
        _ = id_
        pass

    def add_move(self, cards, destination_pos, speed=None):
        """
        Creates cards animation object and stores in into list of moves in the Controller.
        Controller class deletes the animation automatically after it completes.
        :param cards: list of cards to be moved.
        :param destination_pos: tuple with coordinates (x,y) of destination position where cards
                                should be moved.
        :param speed: integer number, on how many pixels card(s) should move per frame.
        """
        if isinstance(cards, list):
            sprites = []
            for card_ in cards:
                if isinstance(card_, card.Card):
                    sprites.append(card_.sprite)
            if len(sprites) != 0:
                self.moves.append(card_sprite.SpriteMove(sprites, destination_pos, speed))
        elif isinstance(cards, card.Card):
            self.moves.append(card_sprite.SpriteMove(cards.sprite, destination_pos, speed))
