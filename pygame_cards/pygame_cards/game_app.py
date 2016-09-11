#!/usr/bin/env python
try:
    import sys
    import os
    import pygame
    import threading
    import json
    import abc

    import gui

    from pygame_cards import globals, controller
except ImportError as err:
    print "Fail loading a module: %s", err
    sys.exit(2)


class RenderThread(threading.Thread):
    """ Represents thread for rendering of game objects """

    def __init__(self, app):
        """
        :param app: object of GameApp class which sprites will be rendered
        """
        threading.Thread.__init__(self)
        self.app = app

    def run(self):
        """ Starts endless loop and renders game objects in it """
        while not self.app.stopped:
            self.app.clock.tick(300)
            self.app.render()
            pygame.display.flip()


class GameApp:
    """ Interface game app class that concrete game classes should inherit """
    __metaclass__ = abc.ABCMeta

    class GuiInterface:
        """ Inner class with GUI interface functions """
        def __init__(self, screen):
            self.screen = screen
            self.gui_list = []

        def show_label(self, position, text, text_size=15, color="black", timeout=3, id_=""):
            label = gui.Title(self.screen, position, text, text_size, color, timeout, id_)
            self.gui_list.append(label)
            return label

        def show_button(self, rectangle, text, callback, text_size=15, color="black", id_=""):
            button = gui.Button(self.screen, rectangle, callback, text, text_size, color, id_)
            self.gui_list.append(button)
            return button

        def hide_by_id(self, id_):
            for g in self.gui_list:
                if hasattr(g, "id") and g.id == id_:
                    self.gui_list.remove(g)
                    break

        def render(self):
            for g in self.gui_list:
                if hasattr(g, 'expired') and g.expired:
                        self.gui_list.remove(g)
                        continue
                g.render()

        def check_mouse(self, down):
            for g in self.gui_list:
                g.check_mouse(pygame.mouse.get_pos(), down)

        def clean(self):
            self.gui_list = []

    def __init__(self, json_name, controller=None):
        """
        :param json_name: path to configuration json file
        """
        # Windows properties that will be set in load_settings_from_json()
        self.title = None
        self.background_color = None
        self.size = None

        globals.settings_json = self.load_json(json_name)
        if globals.settings_json is None:
            raise ValueError('settings json file is not loaded', 'GameApp.__init__')
        self.load_settings_from_json()
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(self.title)
        self.screen = pygame.display.set_mode(self.size)
        self.screen.fill(self.background_color)
        self.clock = pygame.time.Clock()
        self.render_thread = RenderThread(self)
        self.stopped = False
        self.gui_interface = GameApp.GuiInterface(self.screen)
        self.mouse_timestamp = None  # Used for double click calculation
        #self.game_controller = controller
        #self.game_controller.gui_interface = self.gui_interface

    def is_double_click(self):
        if self.mouse_timestamp is None:
            self.mouse_timestamp = pygame.time.get_ticks()
            return False
        else:
            now = pygame.time.get_ticks()
            diff = now - self.mouse_timestamp
            self.mouse_timestamp = now
            if diff < 200:
                return True
        return False

    def process_events(self):
        """ Processes mouse events and quit event """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stopped = True
                self.render_thread.join()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.process_mouse_event(False, self.is_double_click())
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.process_mouse_event(True)

    @staticmethod
    def load_json(path):
        """ Loads json file and returns handle to it
        :param path: path to json file to load
        :return: handle to loaded json file
        """
        with open(path, 'r') as json_file:
            return json.load(json_file)

    def load_settings_from_json(self):
        """ Parses configuration json file and sets properties with values from the json.
            Following window properties are set by this method:
            - Title
            - Background properties
            - Window size
            Other custom game-specific settings should be set by derived classes in load_game_settings_from_json().
        """
        self.title = globals.settings_json["window"]["title"]
        self.background_color = globals.settings_json["window"]['background_color']
        self.size = globals.settings_json["window"]["size"]

    # @abc.abstractmethod
    # def init_gui(self):
    #     """ Initializes default GUI elements. Should be overloaded in derived classes. """
    #     pass

    def process_mouse_event(self, down, double_click=False):
        """ Processes mouse events, invoke mouse events handlers in game_controller and gui_interfaces
        :param down: boolean, True for mouse down event, False for mouse up event
        :param double_click: boolean, True if it's a double click event
        """
        if self.gui_interface is not None:
            self.gui_interface.check_mouse(down)
        if self.game_controller is not None:
            self.game_controller.process_mouse_event(pygame.mouse.get_pos(), down, double_click)

    def init_game(self):
        """ Initializes game and gui objects """
        #self.init_gui()
        self.game_controller.start_game()

    def render(self):
        """ Renders game objects and gui elements """
        pygame.draw.rect(self.screen, self.background_color, (0, 0, self.size[0], self.size[1]))
        if self.game_controller is not None:
            self.game_controller.render_objects(self.screen)
        if self.gui_interface is not None:
            self.gui_interface.render()

    def execute_game_logic(self):
        """ Executes game logic. Should be called recurrently from the game loop """
        if self.game_controller is not None:
            self.game_controller.execute_game()

    def start_render_thread(self):
        """ Starts game rendering thread (object of RenderThread class) """
        self.render_thread.start()

    def run_game_loop(self):
        """ Runs endless loop where game logic and events processing are executed. """
        while 1:
            self.clock.tick(60)
            self.process_events()
            self.execute_game_logic()
            #self.render()

    def execute(self):
        """ Initializes game, starts rendering thread and starts game endless loop """
        self.init_game()
        self.start_render_thread()
        self.run_game_loop()
