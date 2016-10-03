#!/usr/bin/env python
try:
    import sys
    #from enum import IntEnum
except ImportError as err:
    print "Fail loading a module in file:", __file__, "\n", err
    sys.exit(2)


class Rank:
    """ Enums for cards' ranks """
    two = 2
    three = 3
    four = 4
    five = 5
    six = 6
    seven = 7
    eight = 8
    nine = 9
    ten = 10
    jack = 11
    queen = 12
    king = 13
    ace = 14


class Suit:
    """ Enums for cards' suits """
    hearts = 0
    diamonds = 1
    clubs = 2
    spades = 3


class DeckType:
    """ Enums for deck types.
    short - 6,7...,King,Ace
    full - 2,3...,King,Ace
    """
    short = 36,
    full = 52


class GrabPolicy:
    """ Enums for different grab policies of cards' holders."""
    no_grab = 0,
    can_single_grab = 1,
    can_multi_grab = 2


def get_suit_string_from_enum(suit):
    """ Returns unicode character of a card suit
    :param suit: int value that corresponds to one of enums from Suit class
    :return: string with unicode character of the corresponding card suit.
    Empty string if passed suit is not a valid Suit enum
    """
    if suit == Suit.hearts:
        return u'\u2665'
    elif suit == Suit.diamonds:
        return u'\u2666'
    elif suit == Suit.clubs:
        return u'\u2663'
    elif suit == Suit.spades:
        return u'\u2660'
    else:
        return ''
