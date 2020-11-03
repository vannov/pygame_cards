#!/usr/bin/env python
try:
    import sys
    import abc

    from pygame_cards import game_object, card, card_sprite, card_holder, animation
except ImportError as err:
    print("Fail loading a module in file:", __file__, "\n", err)
    sys.exit(2)


class Controller(object, metaclass=abc.ABCMeta):
    """ Abstract interface class that controls game logic and handles user events,
        Should be inherited by concrete game controller classes.

        Following methods are mandatory for all classes that derive from Controller:
            - start_game()
            - process_mouse_event()

        Also these methods are not mandatory, but it can be helpful to define them:
            - execute_game()
            - restart_game()
            - cleanup()

        These methods are called from high level GameApp class. See details about each method below.
        Other auxiliary methods can be added if needed and called from the mandatory methods.
    """

    def __init__(self, objects_list=None, gui_interface=None, settings_json=None):
        """
        Initializes Controller object.
        :param objects_list: list of game objects that should be rendered
        :param gui_interface: gui interface object
        """
        self.rendered_objects = []
        self.animations = []
        if objects_list is not None and isinstance(objects_list, list):
            self.rendered_objects = objects_list
        self.gui_interface = gui_interface
        self.settings_json = settings_json
        self.started = False
        # Make this a color tuple to override game app's background_color.
        self.background_color = None

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
        
        # Advance all animations.
        for animation in self.animations:
            animation.update()

        # Clear completed animations.
        self.animations = [a for a in self.animations if not a.is_completed]

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

    def remove_rendered_object(self, obj):
        """ Removes an object from the list of rendered_objects.
        :param obj: Rendered object to remove.
        """
        self.rendered_objects.remove(obj)

    def add_animation(self, animation):
        """Adds an animation to the list of active animations in the controller.
        :param animation: The animation to add.
        """
        self.animations.append(animation)

    def animate_cards(self, cards, end_pos, speed=None, plotter_fn=None,
                      on_complete=None):
        """Run an animation for a list of Cards or CardsHolder that sends
        them to the given end position in the given amount of time.
        :param cards: Either a list of Cards or a CardsHolder to be animated.
        :param end_pos: Position (x,y) tuple representing where the cards
            should end up.
        :param speed: Speed in pixels / second. If not given, uses
            card.move_speed from settings.json.
        :param plotter_fn: (Optional) lambda(start_pos, end_pos, duration_ms)
            that returns a Plotter object. The plotter's responsibility is to
            determine the position of the cards at any point during the
            animation.
            If not given, a simple LinearPlotter will be used (straight line
            travel, constant speed.)
        :param on_complete: (Optional) lambda(CardsHolder) called when
            animation is over; returns original holder passed in, or, if a
            list of cards was passed, a new holder containing those cards.
        """
        self_ = self

        holder = cards
        temp_holder_required = not isinstance(cards, card_holder.CardsHolder)
        if temp_holder_required:
            if len(cards) == 0: return
            holder = card_holder.StaticOffsetCardsHolder(pos=cards[0].get_pos())
            for card_ in cards:
                holder.add_card(card_)
            self.add_rendered_object(holder)

        def callback():
            if on_complete: on_complete(holder)
            if temp_holder_required: self_.remove_rendered_object(holder)

        if speed is None:
            speed = self.settings_json["card"]["move_speed"]
        start_pos = holder.pos
        duration_ms = animation.expected_duration_ms(start_pos, end_pos, speed)

        if duration_ms > 0:
            # Derive plotter.
            plotter = None
            if plotter_fn is None:
                plotter = animation.LinearPlotter(start_pos, end_pos, duration_ms)
            else:
                plotter = plotter_fn(start_pos, end_pos, duration_ms)
            
            animation_ = animation.CardsHolderAnimation(holder, plotter, callback)
            self.add_animation(animation_)
        else:
            # Short-circuit; don't create animation for 0 ms; just invoke
            # the callback immediately.
            callback()
