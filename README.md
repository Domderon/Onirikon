# Onirikon

Onirikon is a puzzle game where you take control a Frenchman stumbling through the streets of Chania. Eating cheese will increase your weight, while drinking a healthy glass of wine will reduce your weight. In order to pass certain areas you'll need to be either thin (narrow corridors) or big (tornado). If you find the exit, you win.

A genetic algorithm evolves the levels to produce progressively harder levels.
The fitness function optimizes for levels that require more A* search optimizations to find the shortest path.
It guarantees that the (randomly generated) initial trajectory (shown as yellow dots) remains a valid solution through the course of optimization.

Installation:
- requires Python 3.6, numpy, pyGame, PygameGUILib
- run python front.py  (or pythonw front.py on Mac Os -- with Anaconda you may need to install it first with conda install python.app)
- to play: click the Optimize button to start optimization in the background, then choose between Keyboard Mode (arrows) to play manually, or A* Mode to see how the AI solves the generated levels
- press Space to exit

Credits:
- Alberto Alvarez aka "The Genetician"
- David Melhart aka "The Artist"
- Dominik Scherer aka "The Generator"
- Gaël Delalleau aka "The Controller"
- Olivier Delalleau aka "The Explorer"

Produced during the game jam of the "1st International Summer School on Artificial Intelligence and Games" (2018)
