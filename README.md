# pygame_cards

pygame_cards is a Python package for creating simple card games powered by Pygame framework (http://pygame.org/)

The package contains a set of modules that encapsulate Pygame routines and provide a simple API to create a card game with minumum amount of code.

Check out the "examples" folder - it contains implementation of classic "Klondike" solitaire. Here how the game looks like:

<img src="https://github.com/vannov/pygame_cards/blob/int/examples/klondike/klondike.png" width="570" height="470"/>

## Getting Started

There is a template project under "examples" folder that contains a sceleton required to use the framework. The easiest way to get started - copy content of "templates" folder and start adding your code into mygame.py. 

mygame.py script contains comments with description of methods that have to be implemented in order to use the framework.
Template project contains settings.json – another necessary element of a game powered by pygame_cards. Path to this JSON file should be specified when initializing a game with an object of GameApp class from game_app module. Required fields for the JSON file are "window", "card" and "gui". You can also add any amount of custom fields in that file and use them in your code.

There are also mygame_example.py and settings_example.json files in the "templates" folder with some custom code that create very simple game. For more complex example refer to Klondike project under examples/klondike.

### Installing

placeholder...

## Deployment

placeholder...

## Authors

* **Ivan Novosad* - *Initial work* - [vannov](https://github.com/vannov)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details