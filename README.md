# pygame_cards

**pygame_cards** is a Python package for creating simple card games powered by Pygame framework (http://pygame.org/)

The package contains a set of modules that encapsulate Pygame routines and provide a simple API to create a card game with minimum amount of code.

Check out the _examples_ folder - it contains implementation of classic "Klondike" solitaire. Here how the game looks like:

<img src="https://github.com/vannov/pygame_cards/blob/master/examples/klondike/klondike.png" width="570" height="470"/>

## Installation 

####Prerequisites:

Python version 2.7.x: https://www.python.org/downloads/

Pygame version 1.9.x: http://www.pygame.org/download.shtml

There is a known Pygame issue with OS X El Capitan and newer. Because of different versions of SDL_image library, images rendered in a Pygame application look corrupted. The workaround is to downgrade to an older version of SDL_image library. See instructions here: http://stackoverflow.com/a/35385411

####Installation from redistributable:

Download archive with latest available version of **pygame_cards** package from https://github.com/vannov/pygame_cards/releases. Install the package:

- On Mac OS or Linux:
```
sudo pip install pygame_cards-0.1.tar.gz
```

- On Windows (run command prompt as administrator):
```
pip install pygame_cards-0.1.zip
```

####Installation from sources:
To install the **pygame_cards** framework, download this repository, in terminal cd into _pygame_cards_ folder and run command:

```
python setup.py install
```

## Usage

### Getting Started

There is a template project under _examples_ folder that contains a skeleton required to use the framework. The easiest way to get started - copy content of _examples/template_ folder and start adding your code into **mygame.py**. 

**mygame.py** script contains docstrings with description of methods that have to be implemented in order to use the framework.
Template project contains **settings.json** file – another necessary element of a game powered by pygame_cards (see details below).

There are also **mygame_example.py** and **settings_example.json** files in the _examples/template_ folder with some custom code that create very simple game. For more complex example refer to Klondike project under _examples/klondike_.

### JSON settings file

JSON file contains settings used by the framework routines. The path to the JSON file should be specified when creating an object of GameApp class. Mandatory fields for the JSON file are:
- **"window"** with sub-fields: 
    - **"size":** list of 2 integers – width and height of app window in pixels
    - **"title":** string with app title
    - **"background_color"**: list with 3 integers that represent a color  – R, G, B
- **"card"** with sub-fields: 
    - **"size"**: list of 2 integers – width and height of game card
    - **"front_sprite_path"**: string with path to folder with card sprite
    - **"back_sprite_file"**: string with path to file with card back side sprite
    - **"move_speed"**: integer with speed of card move animation, in pixels per frame
 
**Note:** paths in "front_sprite_path" and "back_sprite_file" can be relative to folder with pygame_cards framework, or full paths on your system. Default sprites are included in the framework and are located under _img_ folder. If you are going to use custom sprites for cards, you need to follow the naming convention for your sprite files as under _img/cards_ folder (e.g. "2_of_clubs.png", "ace_of_diamonds.png" etc).
 
These fields should be filled with project specific data. You can also add any amount of custom fields in that file and use them in your code via **settings_json** member of a class derived from the Controller class. For example, see how custom fields "deck", "stack" and "gui" in **mygame_example.py** in _examples/template_ folder.

If some or all of the mandatory fields are missing, the framework will use default values for these fields. Here is JSON with default values of the mandatory fields (**settings.json** from _examples/template_ folder):
```
{
	"window": {
		"size": [570, 460],
		"title": "My Game",
		"background_color": [0, 153, 0]
	},
	"card": {
		"size": [65, 85],
		"front_sprite_path": "img/cards/",
		"back_sprite_file": "img/back-side.png",
		"move_speed": 80
	}
}
```

### Controller class

Controller class from **controller.py** module in the framework is an abstract interface class that controls game logic and handles user events. Each project should contain a concrete class that derive from the Controller class.

An object of class derived from the Controller class has to be passed as an argument when GameApp object is created. See details about GameApp object below.

Following methods are mandatory for all classes that derive from Controller:
- build_objects	
- start_game
- process_mouse_events

Also these methods are not mandatory, but it can be helpful to define them:
- execute_game
- restart_game
- cleanup

In your project you don't need to call these methods directly, they are called from high level GameApp class. See description of each method in the docstrings in **controller.py** module.
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

To create a standalone application from your game, you can use one of third-party tools available, for example: 
- py2app (Mac OS X) https://pythonhosted.org/py2app/
- py2exe (Windows) http://www.py2exe.org/index.cgi/Tutorial
- PyInstaller (Windows, Linux, Mac OS X) http://www.pyinstaller.org/

**Important:** Make sure to include paths to your settings.json file and sprites folder to the package data when exporting your game to an executable. Default cards' sprites files live in the pygame_cards framework under _img_ folder.

Example of creating a Mac OS X app with py2app:

1. Install py2app, see instructions here: https://pythonhosted.org/py2app/install.html

2. In terminal "cd" to your project location and create **setup.py** script with command (replace "main.py" with your entry point file name):

  ```
  py2applet --make-setup main.py
  ```

3. Add paths to the settings.json and cards sprites folder to the created setup.py file (added lines marked with "**ADDED**" comment):
  ```python
    from setuptools import setup
    
    APP = ['main.py']
    DATA_FILES = ['/Library/Python/2.7/site-packages/pygame_cards/img', 'settings.json']  # ADDED
    OPTIONS = {'argv_emulation': True}
    
    setup(
        app=APP,
        data_files=DATA_FILES, # ADDED
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )
  ```

4. Create application with command: 

 ```
 python setup.py py2app
 ```
[![Run on Repl.it](https://repl.it/badge/github/vannov/pygame_cards)](https://repl.it/github/vannov/pygame_cards)
## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details