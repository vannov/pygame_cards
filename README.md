# pygame_cards

pygame_cards is a Python package for creating simple card games powered by Pygame framework (http://pygame.org/)

The package contains a set of modules that encapsulate Pygame routines and provide a simple API to create a card game with minumum amount of code.

Check out the "examples" folder - it contains implementation of classic "Klondike" solitaire. Here how the game looks like:

<img src="https://github.com/vannov/pygame_cards/blob/int/examples/klondike/klondike.png" width="570" height="470"/>

## Installation 

placeholder...

## Usage

### Getting Started

There is a template project under "examples" folder that contains a sceleton required to use the framework. The easiest way to get started - copy content of examples/template folder and start adding your code into mygame.py. 

*mygame.py* script contains docstrings with description of methods that have to be implemented in order to use the framework.
Template project contains *settings.json* – another necessary element of a game powered by pygame_cards (see details below).

There are also mygame_example.py and settings_example.json files in the examples/template folder with some custom code that create very simple game. For more complex example refer to Klondike project under examples/klondike.

### JSON settings file

JSON file contains settings used by the framework routines. The path to the json file should be specified when creating an object of GameApp class. Mandatory fields for the JSON file are:
 - "window" with subfields: "size", "title", "background_color".
 - "card" with subfields: "size", "front_sprite_path", "back_sprite_file", "move_speed".
 
These fields should be filled with project specific data. You can also add any amount of custom fields in that file and use them in your code via settings_json member of a class derived from the Controller class. For example, see how custom fieds "deck", "stack" and "gui" in mygame_example.py in examples/template folder.

Example:

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

### Controller class

Controller class from controller.py module in the framework is an abstract interface class that controls game logic and handles user events. Each project should contain a concrete class that derive from the Controller class.

An object of class derived from the Controller class has to be passed as an argument when GameApp object is created. See details about GameApp object below.

Following methods are mandatory for all classes that derive from Controller:
	- build_objects
	- start_game
	- process_mouse_events

Also these methods are not mandatory, but it can be helpful to define them:
	- execute_game
	- restart_game
	- cleanup

In your project you don't need to call these methods directly, they are called from high level GameApp class. See description of each method in the dosctrings in controller.py module.
Other auxiliary methods can be added if needed and called from the mandatory methods.

### GameApp class

GameApp class controls the application flow and settings. An object of GameApp class has to be created in the entry point of your application (typically in the main() function). 

GameApp constructor takes 2 arguments:
	- json_path: path to JSON settings file
	- game_controller: object of class derived from Controller 

After a GameApp object is created, to start the game simply call execute() method.

Example of the main() method, assuming that there is definition of MyGameController class derived from the Controller:

def main():
    solitaire_app = game_app.GameApp(json_path='settings.json', game_controller=MyGameController())
    solitaire_app.execute()

## Deployment

placeholder...

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details