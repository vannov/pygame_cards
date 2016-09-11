import abc


class Controller:
    """ Interface class that controls game logic and handles user events,
        Should be inherited by concrete game controller classes. """

    __metaclass__ = abc.ABCMeta

    def __init__(self, objects_list=None, gui_interface=None):
        """
        Initializes Controller object.
        :param objects_list: list of game objects
        :param gui_interface: gui interface object
        """
        self.objects = []
        if objects_list is not None and isinstance(objects_list, list):
            self.objects = objects_list
        self.gui_interface = gui_interface
        self.started = False
        self.build_custom_objects()
        # self.grabbed_card = None
        # self.grabbed_card_holder = None

    def build_custom_objects(self):
        """ Should be implemented in derived classes, if needed. Builds custom game objects."""
        pass

    @abc.abstractmethod
    def start_game(self):
        """ Should be implemented in derived classed.
        Creates game objects and initializes the game (deal cards etc.)"""
        pass

    @abc.abstractmethod
    def execute_game(self):
        """ Should be implemented in derived classes.
            Possible things to do in this method:
             - Check game state conditions (game over, win etc.)
             - Run bot (virtual player) actions
             - etc
        """
        pass

    @abc.abstractmethod
    def process_mouse_event(self, pos, down, double_click=False):
        """ Should be implemented in derived classes.
        :param pos: tuple with mouse coordinates (x, y)
        :param down: boolean, True for mouse down event, False for mouse up event
        :param double_click: boolean, True if it's a double click event
        """
        pass

    def render_objects(self, screen):
        """ Renders game objects.
        :param screen: Screen to render objects on.
        """
        if self.objects is not None:
            for obj in self.objects:
                # TODO: add check is instance of GameObject class
                obj.render_all(screen)

    def add_object(self, obj):
        # TODO: uncomment isinstance check
        #if isinstance(obj, GameObject):
        if self.objects is None:
            self.objects = []
        if isinstance(obj, tuple):
            self.objects.extend(obj)
        else:
            self.objects.append(obj)

    @abc.abstractmethod
    def restart_game(self):
        """ Cleans up all objects, rebuilds game object and calls start_game(). """
        pass

    # TODO: implement and uncomment decorator
    #@abc.abstractmethod
    def cleanup(self):
        """ Cleans up game objects and gui when closing or restarting the game. """
        pass
