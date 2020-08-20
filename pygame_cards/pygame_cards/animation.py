#!/usr/bin/env python
try:
    import sys
    import abc
    import math
    import time
except ImportError as err:
    print("Fail loading a module in file:", __file__, "\n", err)
    sys.exit(2)


def expected_duration_ms(point1, point2, speed):
    """Calculate expected duration in milliseconds when traveling from
    point1 to point2 at the given speed.
    :param point1: Point tuple (x,y)
    :param point2: Point tuple (x,y)
    :param speed: Pixels per second
    """
    distance_pixels = distance(point1, point2)
    duration_sec = distance_pixels / speed
    return duration_sec * 1000 # Convert seconds to milliseconds.


def distance(point1, point2):
    """ Calculates distance between two points.
    :param point1: tuple (x, y) with coordinates of the first point
    :param point2: tuple (x, y) with coordinates of the second point
    :return: distance between two points in pixels
    """
    return math.sqrt(math.pow(point1[0] - point2[0], 2) + math.pow(point1[1] - point2[1], 2))


class Plotter(object, metaclass=abc.ABCMeta):
    """Abstract interface class that defines a plotter: an object that
    plots the position of an animated object based on elapsed time.

    Should be inherited by concrete plotter classes.

    Following methods are mandatory for all classes that derive from Plotter:
        - plot(elapsed_ms)
    """
    @abc.abstractmethod
    def plot(self, elapsed_ms) -> ((int, int), bool):
        """Determine the position of some animated object based on
        elapsed time. This method (and the plotter object) does not
        actually move an object; just determines position.

        :param elapsed_ms: the number of milliseconds elapsed since start of animation.
        :return: tuple of (position, boolean of whether animation is completed)
        """
        pass


class XYFunctionPlotter(Plotter, metaclass=abc.ABCMeta):
    """Abstract interface class that defines a plotter that uses a pair of
    functions to plot the x and y positions, respectively, over the elapsed
    time of the animation.

    Should be inherited by concrete plotter classes.

    Following methods are mandatory for all classes that derive from Plotter:
        - get_x_function(start_pos, end_pos, duration_ms)
        - get_y_function(start_pos, end_pos, duration_ms)
    """
    def __init__(self, start_pos, end_pos, duration_ms):
        """Initializes object.
        :param start_pos: Position tuple where plotting begins
        :param end_pos: Position tuple where plotting ends
        """
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.duration_ms = duration_ms
        self.x_fn = self.get_x_function()
        self.y_fn = self.get_y_function()

    @abc.abstractmethod
    def get_x_function(self):
        """Return function that gives the X coordinate of the plotted position
        given the elapsed time.

        :param elapsed_ms: the number of milliseconds elapsed since start of animation.
        :return: lambda function that takes elapsed_ms and returns X position.
        """
        pass

    @abc.abstractmethod
    def get_y_function(self):
        """Return function that gives the Y coordinate of the plotted position
        given the elapsed time.

        :param elapsed_ms: the number of milliseconds elapsed since start of animation.
        :return: lambda function that takes elapsed_ms and returns Y position.
        """
        pass

    def plot(self, elapsed_ms) -> ((int, int), bool):
        """Determine the position of some animated object based on
        elapsed time. This method (and the plotter object) does not
        actually move an object; just determines position.

        :param elapsed_ms: the number of milliseconds elapsed since start of animation.
        :return: tuple of (position, boolean of whether animation is completed)
        """
        if elapsed_ms > self.duration_ms:
            # Animation completed.
            return (self.end_pos, True)
        else:
            plot_pos = (int(self.x_fn(elapsed_ms)), int(self.y_fn(elapsed_ms)))
            return (plot_pos, False)


class LinearPlotter(XYFunctionPlotter):
    """Plots animation as a simple line from start to end at a
    constant speed: no acceleration, deceleration, or fancy flight patterns.
    """
    def __init__(self, start_pos, end_pos, duration_ms):
        """Initializes LinearPlotter object.
        :param start_pos: Position tuple where plotting begins
        :param end_pos: Position tuple where plotting ends
        """
        XYFunctionPlotter.__init__(self, start_pos, end_pos, duration_ms)

    def get_x_function(self):
        """Return function that gives the X coordinate of the plotted position
        given the elapsed time.

        :return: lambda function that takes elapsed_ms and returns X position.
        """
        return self.get_linear_function(self.start_pos[0], self.end_pos[0])

    def get_y_function(self):
        """Return function that gives the Y coordinate of the plotted position
        given the elapsed time.

        :return: lambda function that takes elapsed_ms and returns Y position.
        """
        return self.get_linear_function(self.start_pos[1], self.end_pos[1])

    def get_linear_function(self, start_value, end_value):
        """Return function that plots single line as a function of time.

        :param elapsed_ms: the number of milliseconds elapsed since start of animation.
        :return: lambda function that takes elapsed_ms and maps to value along line.
        """
        if self.duration_ms > 0:
            slope = (end_value - start_value) / self.duration_ms

            def linear_function(elapsed_ms):
                return (slope * elapsed_ms) + start_value
        else:
            def linear_function(elapse_ms):
                return end_value

        return linear_function


class Animation(object, metaclass=abc.ABCMeta):
    """Abstract interface class that defines an animation
    of some sort taking place in the game.

    Should be inherited by concrete animation classes.

    Following methods are mandatory for all classes that derive from Animation:
        - update_pos(pos) - Update position of animated item (whatever it is)
    """
    def __init__(self, plotter, on_complete=None):
        """Initializes object.
        :param plotter: Object that plots position over time for the animation.
        :param on_complete: Optional callback function to call when
            animation completes. Specifically, it's called the first time we
            call update() with an elapsed time that the plotter determines is
            past its expected duration.
            Function takes no arguments and is not expected to return anything.
        """
        self.plotter = plotter
        self.on_complete = on_complete
        self.start_time = time.time()
        self.is_completed = False

    def update(self):
        """Advance the animation forward (based on elapsed time.)
        """
        elapsed_ms = (time.time() - self.start_time) * 1000

        if not self.is_completed:
            (curr_pos, self.is_completed) = self.plotter.plot(elapsed_ms)
            self.update_pos(curr_pos)
            if (self.is_completed and self.on_complete is not None):
                self.on_complete()

    @abc.abstractmethod
    def update_pos(self, new_pos):
        """Abstract method to update the position of whatever is being
        animated.
        :param new_pos: New position (a tuple of x,y coordinates)
        """
        pass


class CardsHolderAnimation(Animation):
    """Animates a card holder from one position to another.
    """
    def __init__(self, holder, plotter, on_complete=None):
        """Initializes object.
        :param holder: CardsHolder object that will be animated.
        :param plotter: Object that plots position over time for the animation.
        :param on_complete: Optional callback function to call when
            animation completes. Specifically, it's called the first time we
            call update() with an elapsed time that the plotter determines is
            past its expected duration.
            Function takes no arguments and is not expected to return anything.
        """
        Animation.__init__(self, plotter, on_complete)
        self.holder = holder
    
    def update_pos(self, new_pos):
        """Update the position of the card holder.
        :param new_pos: New position (a tuple of x,y coordinates)
        """
        self.holder.pos = new_pos
        self.holder.update_position()
