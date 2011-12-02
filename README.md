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
* plotting is pretty slow. i don't really know how other plotting programs
    actually do it, but i'm thinking a speed-up could result from making the
    plotting delta adaptive. instead of evaluating the function (and thus
    drawing a line segment) at every multiple of the delta, we could have the
    delta be a function of |f'(x)|; i.e. small derivative means a larger delta
    and vice versa. then, a bézier curve could be drawn between each pair of
    points, making use of the derivatives to calculate the control points.
    a potential drawback is that cairo might draw curves substantially slower
    than line segments. i dunno. i'll look into it
    
    as it turns out, double-buffering the plots by drawing to image surfaces
    is a horrible idea. a massive speed up came from simply drawing directly to
    the window through the context provided by draw events.
