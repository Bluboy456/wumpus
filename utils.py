# utils.py
#
# Some bits and pieces that are used in different places in the Wumpus
# world code.
#
# Written by: Simon Parsons
# Last Modified: 25/08/20

import random
from enum import Enum

# Representation of directions
class Directions(Enum):
    NORTH = 0
    SOUTH = 1
    EAST  = 2
    WEST  = 3

# representation of game state
class State(Enum):
    PLAY = 0
    WON  = 1
    LOST = 2
    PIT = 3
    WUMPUS = 4

# Class to represent the position of elements within the game
#
class Pose():
    x = 0
    y = 0

class Event(Enum):
    WON = 1
    PIT = 2
    WUMPUS = 3



# Check if two game elements are in the same location
def sameLocation(pose1, pose2):
    if pose1.x == pose2.x:
        if pose1.y == pose2.y:
            return True
        else:
            return False
    else:
        return False

# Pick a location in the range [0, x] and [0, y]
#
# Used to randomize the initial conditions.
def pickRandomPose(x, y):
    p = Pose()
    p.x = random.randint(0, x)
    p.y = random.randint(0, y)

    return p

# print out game state information. Not so useful given the graphical
# display, but might come in handy.
def printGameState(world):
    print("Wumpus:")
    for i in range(len(world.getWumpusLocation())):
        location = world.getWumpusLocation()[i]
        print (location.x, location.y)
        
    print("Link:")
    location = world.getLinkLocation()
    print (location.x, location.y)

    print("Gold:")
    for i in range(len(world.getGoldLocation())):
        location = world.getGoldLocation()[i]
        print (location.x, location.y)

    print("Pits:")
    for i in range(len(world.getPitsLocation())):
        location = world.getPitsLocation()[i]
        print (location.x, location.y)

