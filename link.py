# link.py
#
# The code that defines the behaviour of Link. You should be able to
# do all you need in here, using access methods from world.py, and
# using makeMove() to generate the next move.
#
# Written by: Simon Parsons
# Last Modified: 25/08/20
# Modified by Stuart Jessup 24/12/20 through 28/1/21
# world indexing starts top left.  x direction is DOWN/SOUTH  y direction is RIGHT/EAST

import mdptoolbox
import numpy as np
import sys
from world import World
import config
from dungeon import Dungeon
import random
import utils
from utils import Directions, Pose
import math



class Link():

    def __init__(self, world):

        # Make a copy of the world an attribute, so that Link can
        # query the state of the world
        self.gameWorld = world

        # size of the world - indexed to 0
        self.maxX = self.gameWorld.getMaxX()
        self.maxY = self.gameWorld.getMaxY()
        self.numSquares = (self.maxX+1)*(self.maxY+1)

        #stocastic movement probabilities
        self.prob_ahead = config.directionProbability 
        self.prob_left_error = (1 - self.prob_ahead)/2
        self.prob_right_error = 1 -  self.prob_ahead - self.prob_left_error


        #Arbitrary Constants for occupancy matrix
        self.GOLD = 10
        self.EMPTY = 0
        self.PIT = -5
        self.WUMPUS = -10


        #default reward (cost) value for a square
        self.emptyReward = -0.04   
        self.wumpusReward = -1.1
        self.pitReward = -1.0
        self.goldReward = 1.0
        self.smellyReward = -0.04
        self.glittlerReward = -0.04
        self.windyReward = -0.04

        # What moves are possible.
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]

        # discount factor for value interation
        self.discountFactor = 0.9
        
    def makeMove(self):
        self.gameWorld.updateWumpus()
        self.constructOccupancyMatrix()
        self.constructRewardMatrix()
        self.constructTransisitionMatrix()
        self.valueIteration()

        
        return(self.move_me())




    def constructOccupancyMatrix(self):
        
        # Fill with empty square cost function, same everywhere
        # maxX and maxY are 0 indexed, so add one for array size
        self.OccupancyMatrix = np.full((self.maxX+1, self.maxY+1), self.EMPTY)

        #add Wumpus(s)
        self.wumpusLoc = self.gameWorld.getWumpusLocation()
        for pose in self.wumpusLoc:
            self.OccupancyMatrix[pose.x, pose.y] = self.WUMPUS 

        #add Pit(s)
        pitLoc = self.gameWorld.getPitsLocation()
        for pose in pitLoc:
            self.OccupancyMatrix[pose.x, pose.y] = self.PIT

        #add Gold(s)
        goldLoc = self.gameWorld.getGoldLocation()
        for pose in goldLoc:

            self.OccupancyMatrix[pose.x, pose.y] = self.GOLD      

    #   print ('occupancy matrix:', '\n', self.OccupancyMatrix) #DEBUG

    def constructRewardMatrix(self):
    # Now construct a reward array in a format supported by MPDToolbox
    # THere are four actions per square and, in this case, each has the same reward 
    # So for each element in the occupancy matrix corresponds to a 1 x 4 array 
    # x, y dimensions of occupancy matrix are flattened to 1D in the reward array
    # in the reward array with all elements equal to the reward
    # Add in the guidance bias in a linear fashion acros  the length and/or breadth of the gameworld

        self.RewardArray = np.zeros([self.numSquares,4], dtype=float)
        for x,y in np.ndindex(self.OccupancyMatrix.shape):
            i = x*(self.maxY+1)+y
            # add actual objects
            if self.OccupancyMatrix[x,y] == self.EMPTY:
                self.bias = 0
                if config.biasLeft: self.bias += config.maxBias * (self.maxX - x)/self.maxX
                if config.biasRight: self.bias += config.maxBias * (x+1)/self.maxX
                if config.biasUp: self.bias += config.maxBias * (self.maxY-1 - y)/self.maxY
                if config.biasDown: self.bias  += config.maxBias * (y+1)/self.maxY
                self.RewardArray[i] = [self.emptyReward + self.bias, self.emptyReward + self.bias, 
                                       self.emptyReward + self.bias, self.emptyReward + self.bias]
            elif self.OccupancyMatrix[x,y] == self.GOLD:
                    self.RewardArray[i] = [self.goldReward, self.goldReward, self.goldReward, self.goldReward]
            elif self.OccupancyMatrix[x,y] == self.WUMPUS:
                    self.RewardArray[i] = [self.wumpusReward, self.wumpusReward, self.wumpusReward, self.wumpusReward]
            elif self.OccupancyMatrix[x,y] == self.PIT:
                    self.RewardArray[i] = [self.pitReward, self.pitReward, self.pitReward, self.pitReward]
            else:
                raise Exception("exception: empty matrix")

            
            location = Pose()
            location.x = x
            location.y = y

            # don't change reward for cells adjacent to Gold, Wumpus or Pits
            '''
            # smelly cells (next to Wumpus)
            if self.gameWorld.isSmelly(location):
                self.RewardArray[i] = [self.smellyReward, self.smellyReward, self.smellyReward, self.smellyReward]
            #add reward for glitter cells (next to Gold)
            if self.gameWorld.isGlitter(location):
                self.RewardArray[i] = [self.glittlerReward, self.glittlerReward, self.glittlerReward, self.glittlerReward]
            #add reward for windy cells (next to pit)
            if self.gameWorld.isWindy(location):
                self.RewardArray[i] = [self.windyReward, self.windyReward, self.windyReward, self.windyReward]
            '''
        #print ('Reward Array: ')  #DEBUG
        #print (self.RewardArray)      #DEBUG
        #input() #DEBUG step through each move



    def constructTransisitionMatrix(self):
     # Create 4 sub-arrays covering moves in order right, left, up down
     # There is a sub array for each square containing probabibility of moving to all other squares



        #############################################################################################
        #First look at RIGHT moves (increasing y)
        # create and zero an array of all squares, for each square itself
        right_moves_2D = np.zeros([self.maxX+1, self.maxY+1, self.maxX+1, self.maxY+1], dtype = float)

        for x, y in np.ndindex(self.OccupancyMatrix.shape):
            #current square is self.OccupancyMatrix[current_x,current_y]

            # if we move ahead, as commanded
            # if we are still within the game area and the ahead square is empty
            if y+1 <= self.maxY:
                # yes we can move
                right_moves_2D[x, y, x, y+1] += self.prob_ahead
            else:
            # no we can't, we're stuck
                right_moves_2D[x, y, x, y] += self.prob_ahead

            # if we move left, in error
            if x+1 <= self.maxX:  
                # yes we can move
                right_moves_2D[x, y, x+1, y] += self.prob_left_error

            else:
                # no we can't, stay stuck
                right_moves_2D[x, y, x, y] += self.prob_left_error

            # if we move right, in error
            if x-1 >= 0:
                # yes we can move
                right_moves_2D[x, y, x-1, y] += self.prob_right_error
            else:
                # no we can't, stay stuck
                right_moves_2D[x, y, x, y] += self.prob_right_error

        # convert 2D transistion matrix to 1D
        right_moves_1D = np.empty([self.maxX+1,self.maxY+1, (self.maxX+1) * (self.maxY+1)], dtype = float)
        for x, y in np.ndindex(self.OccupancyMatrix.shape):
            right_moves_1D[x,y]= right_moves_2D[x,y].flatten()

 

        # convert squares array from x,y to linear for mdptoolbox compatibility
        right_moves_mdp = np.empty([self.numSquares, self.numSquares], dtype= float)
        for x, y in np.ndindex(self.OccupancyMatrix.shape):
            i = x*(self.maxY+1)+y    
            for j in range(self.numSquares):
                right_moves_mdp[i,j] = right_moves_1D[x,y,j]    



        #############################################################################################



        #############################################################################################
        #Now LEFT moves (decreasing y)
        # create and zero an array of all squares, for each square itself
        left_moves_2D = np.zeros([self.maxX+1, self.maxY+1, self.maxX+1, self.maxY+1], dtype = float)

        for x, y in np.ndindex(self.OccupancyMatrix.shape):
            # if we move ahead, as commanded and are still within the game area
            if y-1 >= 0 :
                # yes we can move
                left_moves_2D[x, y, x, y-1] += self.prob_ahead
            else:
            # no we can't, we're stuck
                left_moves_2D[x, y, x, y] += self.prob_ahead

            # if we move left, in error
            if x-1 >= 0 :  
                # yes we can move
                left_moves_2D[x, y, x-1, y] += self.prob_left_error

            else:
                # no we can't, stay stuck
                left_moves_2D[x, y, x, y] += self.prob_left_error

            # if we move right, in error
            if x+1 <= self.maxX :
                # yes we can move
                left_moves_2D[x, y, x+1, y] += self.prob_right_error
            else:
                # no we can't, stay stuck
                left_moves_2D[x, y, x, y] += self.prob_right_error


        # convert 2D transistion matrix to 1D
        left_moves_1D = np.empty([self.maxX+1,self.maxY+1, (self.maxX+1) * (self.maxY+1)], dtype = float)
        for x, y in np.ndindex(self.OccupancyMatrix.shape):
            left_moves_1D[x,y]= left_moves_2D[x,y].flatten()         


        # convert squares array from x,y to linear for mdptoolbox compatibility
        left_moves_mdp = np.empty([self.numSquares, self.numSquares], dtype= float)
        for x, y in np.ndindex(self.OccupancyMatrix.shape):
            i = x*(self.maxY+1)+y     
            for j in range(self.numSquares):
                left_moves_mdp[i,j] = left_moves_1D[x,y,j]    


        #############################################################################################


        #############################################################################################
        #Now UP moves (increasing x)
        # create and zero an array of all squares, for each square itself
        up_moves_2D = np.zeros([self.maxX+1, self.maxY+1, self.maxX+1, self.maxY+1], dtype = float)

        for x, y in np.ndindex(self.OccupancyMatrix.shape):
            # if we move ahead, as commanded and are still within the game area
            if x+1 <= self.maxX:
                # yes we can move
                up_moves_2D[x, y, x+1, y] += self.prob_ahead
            else:
            # no we can't, we're stuck
                up_moves_2D[x, y, x, y] += self.prob_ahead

            # if we move left, in error
            if y-1 >= 0:  
                # yes we can move
                up_moves_2D[x, y, x, y-1] += self.prob_left_error

            else:
                # no we can't, stay stuck
                up_moves_2D[x, y, x, y] += self.prob_left_error

            # if we move right, in error
            if y+1 <= self.maxY:
                # yes we can move
                up_moves_2D[x, y, x, y+1] += self.prob_right_error
            else:
                # no we can't, stay stuck
                up_moves_2D[x, y, x, y] += self.prob_right_error   

        # convert 2D transistion matrix to 1D
        up_moves_1D = np.empty([self.maxX+1,self.maxY+1, (self.maxX+1) * (self.maxY+1)], dtype = float)
        for x, y in np.ndindex(self.OccupancyMatrix.shape):
            up_moves_1D[x,y]= up_moves_2D[x,y].flatten()
  

        # convert squares array from x,y to linear for mdptoolbox compatibility
        up_moves_mdp = np.empty([self.numSquares, self.numSquares], dtype= float)
        for x, y in np.ndindex(self.OccupancyMatrix.shape):
            i = x*(self.maxY+1)+y
            #print('x:', str(x), ', y:' , str(y), ', i:', str(i))  #DEBUG         
            for j in range(self.numSquares):
                up_moves_mdp[i,j] = up_moves_1D[x,y,j]    

        #print ('up moves mdp array:', '\n', up_moves_mdp)  #DEBUG


        #############################################################################################



        #############################################################################################
        #Now DOWN moves (decreasing x)
        # create and zero an array of all squares, for each square itself
        down_moves_2D = np.zeros([self.maxX+1, self.maxY+1, self.maxX+1, self.maxY+1], dtype = float)

        for x, y in np.ndindex(self.OccupancyMatrix.shape):
            #current square is self.OccupancyMatrix[current_x,current_y]

            # if we move ahead, as commanded and are still within the game area 
            if x-1 >= 0:
                # yes we can move
                down_moves_2D[x, y, x-1, y] += self.prob_ahead
            else:
            # no we can't, we're stuck
                down_moves_2D[x, y, x, y] += self.prob_ahead

            # if we move left, in error
            if y+1 <= self.maxY:  
                # yes we can move
                down_moves_2D[x, y, x, y+1] += self.prob_left_error

            else:
                # no we can't, stay stuck
                down_moves_2D[x, y, x, y] += self.prob_left_error

            # if we move right, in error
            if y-1 >= 0:
                # yes we can move
                down_moves_2D[x, y, x, y-1] += self.prob_right_error
            else:
                # no we can't, stay stuck
                down_moves_2D[x, y, x, y] += self.prob_right_error   

        # convert 2D transistion matrix to 1D
        down_moves_1D = np.empty([self.maxX+1,self.maxY+1, (self.maxX+1) * (self.maxY+1)], dtype = float)
        for x, y in np.ndindex(self.OccupancyMatrix.shape):
            down_moves_1D[x,y]= down_moves_2D[x,y].flatten()    
 

        # convert squares array from x,y to linear for mdptoolbox compatibility
        down_moves_mdp = np.empty([self.numSquares, self.numSquares], dtype= float)
        for x, y in np.ndindex(self.OccupancyMatrix.shape):
            i = x*(self.maxY+1)+y    
            for j in range(self.numSquares):
                down_moves_mdp[i,j] = down_moves_1D[x,y,j]    


        #############################################################################################



        #Stack the four move arrays to produce the final transisition array for mdptoolbox
        self.transistion_array_mdp = np.array([right_moves_mdp, left_moves_mdp, up_moves_mdp, down_moves_mdp]) 

        #print ('self.transistion_array_mdp:')
        #print (self.transistion_array_mdp)

        # run mdptoolbox check function to confirm arrays are in correct format
        # this is slient if all ok
        mdptoolbox.util.check(self.transistion_array_mdp, self.RewardArray) 

           
    def valueIteration(self):                
        self.valueMatrix = mdptoolbox.mdp.ValueIteration(self.transistion_array_mdp, self.RewardArray, self.discountFactor)
        self.valueMatrix.run()
        
        # print ('Results from mdptoolbox are:') #DEBUG
        #print('Values:\n', self.valueMatrix.V) #DEBUG 
        #print('Policy:\n', self.valueMatrix.policy) #DEBUG


    def move_me(self):
        myPosition = self.gameWorld.getLinkLocation()
        # get policy for my position
        index = myPosition.x *(self.maxY+1) + myPosition.y
        policy = self.valueMatrix.policy[index]

        # mdptoolbox poliocy actions:
        # 0 = left, 1 = right, 2 = up, 3 = down

        # config definitions
        # right = SOUTH, left = NORTH, up = EAST, down = WEST

        #therefore policy to config conversion is
        # 0 = NORTH, 1 = SOUTH 2 = EAST, 3 = WEST
        if policy == 0:
            return Directions.NORTH
        elif policy == 1:
            return Directions.SOUTH
        elif policy == 2:
            return Directions.EAST
        elif policy == 3:
            return Directions.WEST



     

 