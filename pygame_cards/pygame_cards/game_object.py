#!/usr/bin/env python
try:
    import sys
    import abc

    from pygame_cards import enums
except ImportError as err:
    print "Fail loading a module in file:", __file__, "\n", err
    sys.exit(2)


class GameObject(object):
    """ Game object interface, implements Composite design pattern.
        An instance can be a single object (e.g. card) or a structure of objects (e.g. deck).
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, children=[], grab_policy=enums.GrabPolicy.no_grab):
        """
        :param children: list of children objects
        """
        self.children = children
        self.grab_policy = grab_policy

    def add_child(self, child):
        """ Adds child to the list of children objects of a composite object.
        :param child: child to add to the list of children objects
        """
        if isinstance(child, GameObject):
            self.children.append(child)

    def render_all(self, screen):
        """ Renders current object and children objects.
            Internally calls abstract method render() that should be implemented in derived classes.
        :param screen: Screen to render objects on
        """
        for child in self.children:
            child.render(screen)
        self.render(screen)

    @abc.abstractmethod
    def render(self, screen):
        """ Renders current object. Should be implemented in each derived class.
            This method should not care about children objects, they are processed by higher-level
            render() method.
        :param screen: Screen to render objects on
        """
        pass
