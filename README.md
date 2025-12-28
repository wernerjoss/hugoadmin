## hugoadmin.py - a simple Python GUI Tool that helps to manage the content in local Hugo Repositories
![](./hugoadmin.png)
This Program ist a litte Helper that makes content administration (create/edit/check Pages..) of local Hugo Sites a bit easier.  
With this, you can eaysily
-	Choose the Hugo Project you like to work on
-	Create Pages and Blogposts inside the content Folder, based on Templates
-	add custom Templates or use existing Pages as Templates
-	directly edit the newly created Page(s)
-	start a local Hugo Server to view your Changes
-	start the Hugo Build Process

Configuration is done via yaml File ~/.config/hugoadmin.yaml

## Note:
This Program is built and has been tested on Debian Linux 13 (trixie) - it will **NOT** work on Windows !

## Usage:
Before trying to launch the Application (hugoadmin.py) be sure to have the necessary nonstandard-Python Modules installed.  
In Debian 13, these are in the following Packages:
-	python3-pyqt6
-	python3-showinfilemanager
-	python3-yaml

alternativly, the corresponding Modules can be installed from Pypi via pip.

The next step is the adaption of the Configuration File ~/.config/hugoadmin.yaml to the personal needs, the provided file from this Repo can be used as a blueprint.  
Also note that hugoadmin_ui.py must be located in the same Directory as hugoadmin.py.  
The same holds for the 2 provided bash scripts, they are supposed to be executable (chmod +x).

## TODO:
-	prettier GUI :-)
-	realize ability to add custom Templates via GUI
-	(maybe) add procedure to push built Site to Live Server