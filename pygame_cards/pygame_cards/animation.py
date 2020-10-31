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


def get_pulse_plot(a, b, period):
    """Calculates formula to plot a cosine wave with vertical extremes a and b,
    with given x-period.
    :param a: Start position of cosine wave at x=0
    :param b: Opposite y extreme of cosine wave at x=period/2
    :param period: x-period of cosine wave
    :returns: Function to plot cosine wave given x
    """
    def pulse_plot(x):
        amp = (a-b)/2
        rad = (2*math.pi*x)/period
        return (amp*math.cos(rad)) + amp + b

    return pulse_plot


def linear_slope(start_pos, end_pos):
    """Linear slope of line.
    :param start_pos Tuple[int,int]:
    :param end_Pos Tuple[int,int]:
    :returns number or nan: nan if vertical slope
    """
    try:
        return \
            (end_pos[1] - start_pos[1]) \
            / (end_pos[0] - start_pos[0])
    except ZeroDivisionError:
        return math.nan


def radians(start_pos, end_pos):
    """Get angle in radians of line from point to point."""
    y_change = 1 if end_pos[1] > start_pos[1] else -1
    x_change = 1 if end_pos[0] > start_pos[0] else -1

    if start_pos[0] == end_pos[0]: # vertical slope
        return (y_change * math.pi) / 2
    else:
        slope = linear_slope(start_pos, end_pos)
        extra_radians = \
            0 if x_change == 1 \
            else (1 if y_change == 1 else -1) * math.pi
        return math.atan(slope) + extra_radians


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
        :param duration_ms: Total length of animation in milliseconds.
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
            def linear_function(elapsed_ms):
                return end_value

        return linear_function


class LinearToSpiralPlotter(XYFunctionPlotter):
    """Plots animation in two parts: first a line from the start towards
    the end, but skewed to the left or right, and second, an Archimedean
    spiral from the line endpoint in to the final destination.
    """
    def __init__(self, start_pos, end_pos, duration_ms, line_duration_ms,
                 spiral_radius, revolutions, is_clockwise=True):
        """Initializes LinearToSpiralPlotter object.
        :param start_pos: Position tuple where plotting begins
        :param end_pos: Position tuple where plotting ends
        :param duration_ms: Total length of animation in milliseconds.
        :param line_duration_ms: Length of time in ms spent on linear approach
            to spiral. Deducted from duration_ms.
        :param spiral_radius: Outer radius of spiral.
        :param revolutions: Approximate number of revolutions in the spiral.
        :param is_clockwise bool: Whether spiral goes clockwise (otherwise,
            it goes counter-clockwise.)
        """
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.duration_ms = duration_ms
        self.line_duration_ms = line_duration_ms
        self.spiral_radius = spiral_radius
        self.revolutions = revolutions
        self.spiral_dir = -1 if is_clockwise else 1
        # theta_direct: direct line angle (opposite of approach)
        self.theta_direct = radians(start_pos, end_pos)
        # theta_spiral_start: angle where inward spiral should begin.
        #   90 degrees clockwise or counter-clockwise from angle of approach.
        self.theta_spiral_start = \
            self.theta_direct + (self.spiral_dir * (math.pi/2))
        self.spiral_start_pos = self.get_spiral_start_pos()
        self.linear_approach_plotter = \
            LinearPlotter(start_pos, self.spiral_start_pos, line_duration_ms)
        # theta_full_spiral: radians for full spiral travel from start to 
        #   center point, including all revolutions.
        self.theta_full_spiral = \
            (self.theta_direct + (math.pi/2)) \
            + (2 * math.pi * revolutions)
        self.velocity = spiral_radius / self.theta_full_spiral
        # theta_modifier: component of plot functions that is a little
        #   different if going clockwise vs counter-clockwise.
        self.theta_modifier = \
            0 if self.spiral_dir == 1 \
            else -2 * self.theta_spiral_start
        XYFunctionPlotter.__init__(self, start_pos, end_pos, duration_ms)

    def get_spiral_start_pos(self):
        """Position at which the spiral begins."""
        x = \
            (self.spiral_radius * math.cos(self.theta_spiral_start)) \
            + self.end_pos[0]
        y = \
            (self.spiral_radius * math.sin(self.theta_spiral_start)) \
            + self.end_pos[1]
        return x,y

    def get_spiral_x_function(self):
        g = self.spiral_dir
        v = self.velocity
        th_mod = self.theta_modifier
        d = self.duration_ms
        c = 0 # offset from center - should be 0
        w = 1 # angular velocity
        th = self.theta_full_spiral

        def x_function(t):
            return \
                (
                    g \
                    * (((v * (d-t) * th) / d) + c)
                    * math.cos(((w * (d-t) * th) / d) + th_mod)
                ) \
                + self.end_pos[0]

        return x_function

    def get_spiral_y_function(self):
        v = self.velocity
        th_mod = self.theta_modifier
        d = self.duration_ms
        c = 0 # offset from center - should be 0
        w = 1 # angular velocity
        th = self.theta_full_spiral

        def y_function(t):
            return \
                (
                    (((v * (d-t) * th) / d) + c)
                    * math.sin(((w * (d-t) * th) / d) + th_mod)
                ) \
                + self.end_pos[1]

        return y_function

    def get_x_function(self):
        """Return function that plots line-to-spiral as a function of time.

        :param elapsed_ms: the number of milliseconds elapsed since start of animation.
        :return: lambda function that takes elapsed_ms and maps to x position.
        """
        if self.duration_ms > 0:
            linear_x_function = self.linear_approach_plotter.get_x_function()
            spiral_x_function = self.get_spiral_x_function()
            
            def x_function(elapsed_ms):
                if elapsed_ms <= self.line_duration_ms:
                    # Still in the linear approach part of the plot.
                    return linear_x_function(elapsed_ms)
                else:
                    return spiral_x_function(elapsed_ms - self.line_duration_ms)

            return x_function
        else:
            def x_function(elapsed_ms):
                return self.end_pos[0]

            return x_function

    def get_y_function(self):
        """Return function that plots line-to-spiral as a function of time.

        :param elapsed_ms: the number of milliseconds elapsed since start of animation.
        :return: lambda function that takes elapsed_ms and maps to y position.
        """
        if self.duration_ms > 0:
            linear_y_function = self.linear_approach_plotter.get_y_function()
            spiral_y_function = self.get_spiral_y_function()

            def y_function(elapsed_ms):
                if elapsed_ms <= self.line_duration_ms:
                    # Still in the linear approach part of the plot.
                    return linear_y_function(elapsed_ms)
                else:
                    return spiral_y_function(elapsed_ms - self.line_duration_ms)

            return y_function
        else:
            def y_function(elapsed_ms):
                return self.end_pos[0]

            return y_function



class Animation(object, metaclass=abc.ABCMeta):
    """Abstract interface class that defines an animation
    of some sort taking place in the game.

    Should be inherited by concrete animation classes.

    Following members are mandatory for all classes that derive from Animation:
        - update() - Update animation
    """
    def __init__(self, on_complete=None):
        """Initializes object.
        :param on_complete: Optional callback function to call when
            animation completes.
            Function takes no arguments and is not expected to return anything.
        """
        self.on_complete = on_complete
        self.start_time = time.time()
        self._is_completed = False

    @property
    def is_completed(self):
        return self._is_completed

    @is_completed.setter
    def is_completed(self, value):
        newly_complete = value and not self._is_completed
        self._is_completed = value
        if newly_complete and self.on_complete is not None:
            self.on_complete()

    @abc.abstractmethod
    def update(self):
        """Advance the animation forward."""
        pass


class PositionAnimation(Animation, metaclass=abc.ABCMeta):
    """Abstract class that defines an animation
    from one position to another.

    Should be inherited by concrete animation classes.

    Following methods are mandatory for all classes that derive from PositionAnimation:
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
        Animation.__init__(self, on_complete)
        self.plotter = plotter

    def update(self):
        """Advance the animation forward (based on elapsed time.)
        """
        elapsed_ms = (time.time() - self.start_time) * 1000

        if not self.is_completed:
            (curr_pos, is_completed) = self.plotter.plot(elapsed_ms)
            self.update_pos(curr_pos)
            self.is_completed = is_completed

    @abc.abstractmethod
    def update_pos(self, new_pos):
        """Abstract method to update the position of whatever is being
        animated.
        :param new_pos: New position (a tuple of x,y coordinates)
        """
        pass


class CardsHolderAnimation(PositionAnimation):
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
        PositionAnimation.__init__(self, plotter, on_complete)
        self.holder = holder
    
    def update_pos(self, new_pos):
        """Update the position of the card holder.
        :param new_pos: New position (a tuple of x,y coordinates)
        """
        self.holder.pos = new_pos
        self.holder.update_position()


class ColorPulseAnimation(Animation):
    """Pulses back and forth between two colors.
    """
    def __init__(self, color1, color2, period_ms, set_color, on_complete=None):
        """Initialize new instance of ColorPulseAnimation.
        :param color1: First color in the color pulse (start of vacillation.)
        :param color2: Second color in the color pulse (end of vacillation.)
        :param period_ms: Duration in milliseconds of full pulse from color1 to
            color2 and back to color1.
        :param set_color: Callback to set the color based on the animation's
            current color. Receives one parameter: a color tuple. Returns nothing.
        :param on_complete: Optional callback that occurs when animation completes.
        """
        Animation.__init__(self, on_complete)
        self.color1 = color1
        self.color2 = color2
        self.period_ms = period_ms
        self.set_color = set_color
        self.r_plot = get_pulse_plot(color1[0], color2[0], period_ms)
        self.g_plot = get_pulse_plot(color1[1], color2[1], period_ms)
        self.b_plot = get_pulse_plot(color1[2], color2[2], period_ms)

    def update(self):
        """Advance the animation forward (based on elapsed time.)
        """
        if not self.is_completed:
            elapsed_ms = (time.time() - self.start_time) * 1000
            color = (self.r_plot(elapsed_ms), self.g_plot(elapsed_ms), self.b_plot(elapsed_ms))
            self.set_color(color)
