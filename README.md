# partillery
An artillery game written using Pygame.

### Demo 
(Links to YouTube)

[![IMAGE ALT TEXT](http://img.youtube.com/vi/HO-DJegOd1w/0.jpg)](http://www.youtube.com/watch?v=HO-DJegOd1w "Partillery")


### Background:

Pygame is minimal game framework for Python. It provides basic drawing functions and 'Sprites', which are movable objects that can load custom images and detect object collsions.

This game doesn't heavily rely on Sprites. Why? Well, several old 8-bit NES type games depended on the concept of 'Tiles', which are rectangular (or often square) blocks of objects. Detecting collsions among such objects is as simple as detecting overlap between rectangles.

Instead, the focus here is on detecting pixel-perfect collisions between an irregular surface with a projectile.

Without Sprites, everthing needs to be painted and repainted on the screen with your own code, e.g. redrawing a small bit of the sky in the area where the terrain is blown away.  

### Cool stuff:
- A randomly generated terrain (macro shapes 'Hill', 'Valley' and 'Cliff' superimposed with a custom Perlin noise function which generates an undulated surface).
- Tanks behave almost like rigid bodies and can roll along the terrain as well as rest on concave / convex surfaces.
- Explosions properly cut the terrain. The cut area can actually be traversed by the tank afterwards.
- The ground falls as particles under gravity.
- Tank turrets can be moved with the mouse, as can the controls.
- Projectile motion (well)
- Explosions can use maths functions to generate nice effects (TODO).

### Graphics:
Everything was painstakingly designed in GIMP (Ubuntu), including the backgrounds, objects, logo and the control panel.

The game is far from finished / perfect, but like all things good, this is a cool journey.








