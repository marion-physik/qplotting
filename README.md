# What is this?
A first prototype for the plotting software. 

## Scope 

The goal for the plotting software is to provide convenient plotting, live during experiments and after the experiments are done. It should provide a way to gain an overview over multiple datasets easily and help avoid repetition in the workflow by having to create the same plot manually multiple times. 

Creating plots to gain an overview over data and standard plots will require minimal effort. To facilitate that in all relevant contexts the software will have a graphical user interface and an option to interact with all relevant classes and functions through pythons scripts. 

Plots can be exported and are always reproducible. A file containing very step done to get from raw data to the plot can be exported.

Complex analysis functions can be implemented and added by users. The software will provide a few common analysis functions. Giving the option for users to provide own analysis functions will hopefully also future prove the software. 

## Out of Scope

The software will not provide complex analysis functions.

A decision on how exactly plots will be implemented has not been made jet. Very complex plots might need complex configuration by the user or be out of scope.

Exported plots are not intended for publication but as a placeholder.

# How to use this

Install via `pip install git+https://git-ce.rwth-aachen.de/qutech/individual-projects/plotting-software`

The package is called loter untill I find a better name.

To try out the package open a jupyter notebook (a .ipynb file) and run the following lines of code in it.
```
from loter import manager_class
manager_class.ManagerClass()
```

## Jupyter Notebooks

Running a jupyter notebook is necessary to use this software.
Depending on your IDE this might me easier or harder to do. 

### VS Code
VS Code does natively support jupyter notebooks. To work with Python in Jupyter Notebooks, you must activate an Anaconda environment in VS Code, or another Python environment in which you've installed the Jupyter package (pip install jupyter). 
To select an environment, use the Python: Select Interpreter command from the Command Palette (Ctrl+Shift+P).

### Spyder
Spyder does not natively support jupyter notebooks. To work with jupyter in spyder the spyder notebook plugin might be helpful ( pip install spyder-notebook), alternatively, switch to a different IDE. 

### GNU Emacs
If you are using GNU Emacs you do not need my help with figuring this out.


*You are welcome to test this. Please contact Marion with any feedback, feature requests and bug reports.*

