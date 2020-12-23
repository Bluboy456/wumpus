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
from world import World
import config
from dungeon import Dungeon
import random
import utils
from utils import Directions
#import mdptoolbox

class Pose():
    x = 0
    y = 0

class Link():

    def __init__(self, dungeon):

        # Make a copy of the world an attribute, so that Link can
        # query the state of the world
        self.gameWorld = dungeon

        # size of the world - indexed to 0
        self.maxX = self.gameWorld.getMaxX()
        self.maxY = self.gameWorld.getMaxY()

        #default reward (cost) value for a square
        self.cost = -0.04   
        self.wumpusReward = -1.1
        self.pitReward = -1.0
        self.goldReward = 1.0

        # What moves are possible.
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
        
    def makeMove(self):
        # This is development code for MDP algorithm, it does not return any commands yet
        self.RewardMatrix() # construct reward matrix
        '''
        # Commands are returned by placeholder code below, which always moves Link
        # directly towards the gold.
        # 
        # Get the location of the gold.
        allGold = self.gameWorld.getGoldLocation()
        if len(allGold) > 0:
            nextGold = allGold[0]
        myPosition = self.gameWorld.getLinkLocation()
        # If not at the same x coordinate, reduce the difference
        if nextGold.x > myPosition.x:
            return Directions.EAST
        if nextGold.x < myPosition.x:
            return Directions.WEST
        # If not at the same y coordinate, reduce the difference
        if nextGold.y > myPosition.y:
            return Directions.NORTH
        if nextGold.y < myPosition.y:
            return Directions.SOUTH
        '''
    def RewardMatrix(self):
        
        # Fill with empty square cost function, same everywhere
        # maxX and maxY are 0 indexed, so add one for array size
        self.RewardArray = np.full((self.maxX+1, self.maxY+1), self.cost)

        #add Wumpus(s)
        wumpusLoc = self.gameWorld.getWumpusLocation()
        for pose in wumpusLoc:
            #print ('Wumpus at ' + str (pose.x) + str (pose.y)) #DEBUG
            self.RewardArray[pose.x, pose.y] = self.wumpusReward   

        #add Pit(s)
        pitLoc = self.gameWorld.getPitsLocation()
        for pose in pitLoc:
            #print ('Pit at ' + str (pose.x) + str (pose.y)) #DEBUG
            self.RewardArray[pose.x, pose.y] = self.pitReward 

        #add Gold(s)
        goldLoc = self.gameWorld.getGoldLocation()
        for pose in goldLoc:
            #print ('Gold at ' + str (pose.x) + str (pose.y))  #DEBUG
            self.RewardArray[pose.x, pose.y] = self.goldReward          

        #print(self.RewardArray) #DEBUG
