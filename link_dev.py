#! /usr/bin/env python
# link.py
#
# The code that defines the behaviour of Link. You should be able to
# do all you need in here, using access methods from world.py, and
# using makeMove() to generate the next move.
#
# Written by: Simon Parsons
# Last Modified: 25/08/20
# Modified by Stuart Jessup 24/12/20 through 28/1/21


import numpy as np
import world
import random
import utils
from utils import Directions
import mdptoolbox

class Link():

    def __init__(self, dungeon):

        # Make a copy of the world an attribute, so that Link can
        # query the state of the world
        self.gameWorld = dungeon

        # What moves are possible.
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
    
    def RewardMatrix(self):
        cost = -0.04
        self.RewardArray = np.full((self.gameWorld.MaxX, self.gameWorld.MaxY), cost)
        print (self.RewardArray)
      

def main():
    my_Link = Link()
    my_Link.RewardMatrix()


if __name__ == "__main__":
    main()