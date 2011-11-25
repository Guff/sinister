sinister
========
sinister is a simple, interactive, python-based plotting/graphing application.
Hopefully, it will be fairly quick and easy to customize.

Possible future features include:
* embedded interactive ython interpreter
* history/logging
* configuration file, likely done as a python script

under the hood
--------------
sinister is written for python 3, and uses pygobject in order to make use of
GTK and cairo et al.

issues
------
well, right now, it doesn't really do much. and there are still issues with the
few things it does do:
* plotting works, but there are a few kinks (most obvious is how it handles
    discontinuities)
* the status bar currently uses a monospace font out of programmer laziness. it
    needs to be redone somewhat so that it can handle variable-width fonts
    without acting spastically
* well, there isn't all that much in terms of a user interface. hopefully,
    that will change soon, as it is a top priority
