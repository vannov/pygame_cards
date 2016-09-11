#!usr/bin/env python
try:
    import sys
    import abc
    import pygame
    from threading import Timer
except ImportError as err:
    print "Fail loading a module: %s", err
    sys.exit(2)


class AbstractGUI:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def check_mouse(self, p, down):
        pass


class Button(AbstractGUI):
    inner_color = (191, 191, 191)
    inner_pressed_color = (153, 153, 153)
    frame_color = (77, 77, 77)
    frame_thickness = 1
    frame_pressed_thickness = 2
    text_color = (0, 0, 0)
    text_pressed_color = (255, 255, 255)
    text_margin = (3, 3)

    def __init__(self, screen, rect, onclick, text=""):
        self.screen = screen
        self.text = text
        self.onclick = onclick
        self.font = pygame.font.SysFont('arial', 15, bold=1)
        self.text_surface = self.font.render(self.text, True, Button.text_color)
        text_size = self.font.size(self.text)
        self.rect = (rect[0], rect[1], text_size[0] + 2 * Button.text_margin[0], text_size[1] + 2 * Button.text_margin[1])
        self.text_pos = self.rect[0] + (self.rect[2] - text_size[0])/2, self.rect[1] + (self.rect[3] - text_size[1])/2
        self.pressed = False

    def render(self):
        if self.pressed:
            pygame.draw.rect(self.screen, Button.inner_pressed_color, self.rect)
            pygame.draw.rect(self.screen, Button.frame_color, self.rect, Button.frame_pressed_thickness)
        else:
            pygame.draw.rect(self.screen, Button.inner_color, self.rect)
            pygame.draw.rect(self.screen, Button.frame_color, self.rect, Button.frame_thickness)

        self.screen.blit(self.text_surface, self.text_pos)

    def check_mouse(self, p, down):
        if p[0] > self.rect[0] and p[0] < self.rect[0] + self.rect[2] and \
                        p[1] > self.rect[1] and p[1] < self.rect[1] + self.rect[3]:
            if down:
                self.pressed = True
            else:
                self.pressed = False
                self.onclick()


class Title(AbstractGUI):
    def __init__(self, screen, pos, text="", timeout=3):
        self.text = text
        self.font = pygame.font.SysFont('arial', 15, bold=1)
        self.pos = pos
        self.screen = screen
        self.expired = False
        if timeout != 0:
            self.timer = Timer(timeout, self.expire)
            self.timer.start()

    def expire(self):
        self.expired = True

    def render(self):
        if self.text != "":
            text_surface = self.font.render(self.text, True, Button.text_color)
            self.screen.blit(text_surface, self.pos)

    """ No action on click for text label """
    def check_mouse(self, p, down):
        pass


