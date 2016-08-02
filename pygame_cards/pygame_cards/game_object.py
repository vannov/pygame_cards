import abc


class GameObject:
    """ Game object interface, implements Composite design pattern.
        An instance can be a single object (e.g. card) or a structure of objects (e.g. deck).
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, composite=False, children=[]):
        """
        :param composite: boolean, False for single objects, True for composite objects with children
        :param children: list of children objects
        """
        self.composite = composite
        self.children = children

    def add_child(self, child):
        """ Adds child to the list of children objects of a composite object.
        :param child: child to add to the list of children objects
        """
        if self.composite is not True and isinstance(child, GameObject):
            self.children.append(child)

    def render(self, screen):
        """ Renders current object and children objects.
            Internally calls abstract method _render() that should be implemented in derived classes.
        :param screen: Screen to render objects on
        """
        if self.composite:
            for ch in self.children:
                ch.render(screen)
            self._render(screen)

    @abc.abstractmethod
    def _render(self):
        """ Renders current object. Should be implemented in each derived class.
            This method should not care about children objects, they are processed by higher-level render() method.
        """
        pass
