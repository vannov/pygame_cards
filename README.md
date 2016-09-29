# pygame_cards

**pygame_cards** is a Python package for creating simple card games powered by Pygame framework (http://pygame.org/)

The package contains a set of modules that encapsulate Pygame routines and provide a simple API to create a card game with minimum amount of code.

Check out the _examples_ folder - it contains implementation of classic "Klondike" solitaire. Here how the game looks like:

<img src="https://github.com/vannov/pygame_cards/blob/int/examples/klondike/klondike.png" width="570" height="470"/>

## Installation 

Prerequisites:
Python version 2.7.x: https://www.python.org/downloads/
Pygame version 1.9.x: http://www.pygame.org/download.shtml


To install the **pygame_cards** framework, download this repository, in terminal cd into _pygame_cards_ folder and run this command:

```
python setup.py install
```

## Usage

### Getting Started

There is a template project under _examples_ folder that contains a skeleton required to use the framework. The easiest way to get started - copy content of _examples/template_ folder and start adding your code into _mygame.py_. 

**mygame.py** script contains docstrings with description of methods that have to be implemented in order to use the framework.
Template project contains **settings.json** – another necessary element of a game powered by pygame_cards (see details below).

There are also _mygame_example.py_ and _settings_example.json_ files in the _examples/template_ folder with some custom code that create very simple game. For more complex example refer to Klondike project under _examples/klondike_.

### JSON settings file

JSON file contains settings used by the framework routines. The path to the json file should be specified when creating an object of GameApp class. Mandatory fields for the JSON file are:
- **"window"** with sub-fields: "size", "title", "background_color".
- **"card"** with sub-fields: "size", "front_sprite_path", "back_sprite_file", "move_speed".
 
These fields should be filled with project specific data. You can also add any amount of custom fields in that file and use them in your code via **settings_json** member of a class derived from the Controller class. For example, see how custom fields "deck", "stack" and "gui" in _mygame_example.py_ in _examples/template_ folder.

Example:

```
{
	"window": {
		"size": [680, 400],
		"title": "My Game",
		"background_color": [0, 153, 0]
	},
	"card": {
		"size": [65, 85],
		"front_sprite_path": "img/cards/",
		"back_sprite_file": "img/back-side.png",
		"move_speed": 50
	},
	"deck": {
		"position": [10, 10],
		"offset": [0.2, 0]
	},
	"stack": {
        "position": [90, 10],
        "offset": [15, 0]
    },
    "gui": {
        "restart_button": [10, 360, 50, 25]
    }
}
```

### Controller class

Controller class from _controller.py_ module in the framework is an abstract interface class that controls game logic and handles user events. Each project should contain a concrete class that derive from the Controller class.

An object of class derived from the Controller class has to be passed as an argument when GameApp object is created. See details about GameApp object below.

Following methods are mandatory for all classes that derive from Controller:
- build_objects	
- start_game
- process_mouse_events

Also these methods are not mandatory, but it can be helpful to define them:
- execute_game
- restart_game
- cleanup

In your project you don't need to call these methods directly, they are called from high level GameApp class. See description of each method in the docstrings in _controller.py_ module.
Other auxiliary methods can be added if needed and called from the mandatory methods.

### GameApp class

GameApp class controls the application flow and settings. An object of GameApp class has to be created in the entry point of your application (typically in the main() function). 

GameApp constructor takes 2 arguments:
- **json_path**: path to JSON settings file
- **game_controller**: object of class derived from Controller 

After a GameApp object is created, to start the game simply call execute() method.

Example of the main() method, assuming that there is definition of MyGameController class derived from the Controller:

```python
def main():
    solitaire_app = game_app.GameApp(json_path='settings.json', game_controller=MyGameController())
    solitaire_app.execute()
```

## Deployment

placeholder...

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details