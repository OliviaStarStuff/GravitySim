# GravitySim
An N body simulation of the solar system

Coded this is a relatively short period of time following a tutorial to understand how to adapt the gravitational equation to cartesian coordiantes.

Controls are:

* Up/Down/Left/Right moves camera
* Z/X zooms camera in/our
* R resets view and scale
* C/V speeds/slows time (Will result in wonky physics for objects orbiting closely to another body such as earth-moon)
* F locks camera to planet
* G switches between all planetary bodies.

Areas to improve:
* find a way to determine barycenter of two bodies and lock camera to barycenter.
* optimize calculation so bodies that are close to each other can be simulated properly at high speeds.
* Include collision mechanics
