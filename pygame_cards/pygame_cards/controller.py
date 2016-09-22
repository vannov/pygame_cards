import abc

from pygame_cards import game_object

class Controller:
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

        These methods are called from higher level GameApp class. See details about each method below.
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
        if objects_list is not None and isinstance(objects_list, list):
            self.rendered_objects = objects_list
        self.gui_interface = gui_interface
        self.settings_json = settings_json
        self.started = False

        # Dictionary where any custom objects needed can be stored
        self.custom_dict = dict()

    @abc.abstractmethod
    def build_objects(self):
        """ Create permanent game objects (deck of cards, players etc.) and GUI elements in this method.
            This method is executed during creation of GameApp object.
        """
        pass

    @abc.abstractmethod
    def start_game(self):
        """ Put game initialization code here. For example: dealing of cards, initialization of game timer etc.
            This method is triggered by GameApp.execute().
        """
        pass

    @abc.abstractmethod
    def process_mouse_event(self, pos, down, double_click):
        """ Put code that handles mouse events here. For example: grab card from a deck on mouse down event,
            drop card to a pile on mouse up event etc.
            This method is called every time mouse event is detected.
            :param pos: tuple with mouse coordinates (x, y)
            :param down: boolean, True for mouse down event, False for mouse up event
            :param double_click: boolean, True if it's a double click event
        """
        pass

    def execute_game(self):
        """ This method is called in an endless loop started by GameApp.execute().
        IMPORTANT: do not put any "heavy" computations in this method! It is executed frequently in an endless loop
        during the app runtime, so any "heavy" code will slow down the performance.
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
            This method can be used after game over or as a handler of "Restart" button, for example.
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

    def add_object(self, obj):
        if self.rendered_objects is None:
            self.rendered_objects = []
        if isinstance(obj, tuple):
            self.rendered_objects.extend(obj)
        elif isinstance(obj, game_object.GameObject):
            self.rendered_objects.append(obj)
