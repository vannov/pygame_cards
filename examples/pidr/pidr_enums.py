#!/usr/bin/env python
from enum import Enum

talon = 2

class PidrCardType(Enum):
    talon = 0
    open = 1
    regular = 2

class PidrGameStage(Enum):
    dealing = 0
    main = 1

class PidrGameRules(Enum):
    soft = 0
    strict = 1

class GamePhase(Enum):
    dealing = 0
    playing = 1