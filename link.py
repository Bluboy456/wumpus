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
import sys
from world import World
import config
from dungeon import Dungeon
import random
import utils
from utils import Directions, Pose
#import mdptoolbox


class Link():

    def __init__(self, dungeon):

        # Make a copy of the world an attribute, so that Link can
        # query the state of the world
        self.gameWorld = dungeon

        # size of the world - indexed to 0
        self.maxX = self.gameWorld.getMaxX()
        self.maxY = self.gameWorld.getMaxY()
        self.numSquares = (self.maxX+1)*(self.maxY+1)

        #stocastic movement probabilities
        self.prob_ahead = 0.8
        self.prob_left_error = 0.1
        self.prob_right_error = 0.1


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

        # What moves are possible.
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
        
    def makeMove(self):
        #development code for MDP algorithm, it does not return any commands yet
        self.constructOccupancyMatrix()
        self.constructRewardMatrix()
        self.constructTransisitionMatrix()




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
    def constructOccupancyMatrix(self):
        
        # Fill with empty square cost function, same everywhere
        # maxX and maxY are 0 indexed, so add one for array size
        self.OccupancyMatrix = np.full((self.maxX+1, self.maxY+1), self.EMPTY)

        #add Wumpus(s)
        wumpusLoc = self.gameWorld.getWumpusLocation()
        for pose in wumpusLoc:
            #print ('Wumpus at ' + str (pose.x) + str (pose.y)) #DEBUG
            self.OccupancyMatrix[pose.x, pose.y] = self.WUMPUS 

        #add Pit(s)
        pitLoc = self.gameWorld.getPitsLocation()
        for pose in pitLoc:
            #print ('Pit at ' + str (pose.x) + str (pose.y)) #DEBUG
            self.OccupancyMatrix[pose.x, pose.y] = self.PIT

        #add Gold(s)
        goldLoc = self.gameWorld.getGoldLocation()
        for pose in goldLoc:
            #print ('Gold at ' + str (pose.x) + str (pose.y))  #DEBUG
            self.OccupancyMatrix[pose.x, pose.y] = self.GOLD        

        print ('occupnacy matrix:')
        print(self.OccupancyMatrix) #DEBUG

    def constructRewardMatrix(self):
    # Now construct a reward array in a format supported by MPDToolbox
    # THere are four actions per square and, in this case, each has the same reward 
    # So for each element in the occupancy matrix corresponds to a 1 x 4 array 
    # x, y dimensions of occupancy matrix are flattened to 1D in the reward array
    # in the reward array with all elements equal to the reward

        self.RewardArray = np.zeros([self.numSquares,4], dtype=int)
        print ('maxX: ', str(self.maxX), 'maxY: ', str(self.maxY))
        for x,y in np.ndindex(self.OccupancyMatrix.shape):
            i = x*(self.maxY+1)+y
            #print ('x:', str(x), 'y:', str(y), 'i:', str(i)) #DEBUG
            if self.OccupancyMatrix[x,y] == self.EMPTY:
                self.RewardArray[i] = [self.emptyReward, self.emptyReward, self.emptyReward, self.emptyReward]
            elif self.OccupancyMatrix[x,y] == self.GOLD:
                    self.RewardArray[i] = [self.goldReward, self.goldReward, self.goldReward, self.goldReward]
            elif self.OccupancyMatrix[x,y] == self.WUMPUS:
                    self.RewardArray[i] = [self.wumpusReward, self.wumpusReward, self.wumpusReward, self.wumpusReward]
            elif self.OccupancyMatrix[x,y] == self.PIT:
                    self.RewardArray[i] = [self.pitReward, self.pitReward, self.pitReward, self.pitReward]
            else:
                raise Exception("error in coccupancy matrix")

        #print ('MDP Reward Array: ')  #DEBUG
        #print (self.RewardArray)      #DEBUG



    def constructTransisitionMatrix(self):
     # Create 4 sub-arrays covering moves in order right, left, up down
     # There is a sub array for each square containing probabibility of moving to all other squares

     #First look at RIGHT moves
        # create and zero an array of all squares, for each square itself
        self.right_moves = np.zeros([self.maxX+1, self.maxY+1, self.maxX+1, self.maxY+1], dtype = float)

        for x, y in np.ndindex(self.OccupancyMatrix.shape):
            #current square is self.OccupancyMatrix[current_x,current_y]

            # if we move ahead, as commanded
            # if we are still within the game area and the ahead square is empty
            if x+1 <= self.maxX and self.OccupancyMatrix [x+1, y] == self.EMPTY: #ok because python evaluates 'and' lazily
                # yes we can move
                self.right_moves[x, y, x+1, y] += self.prob_ahead
            else:
            # no we can't, we're stuck
                self.right_moves[x, y, x, y] += self.prob_ahead

            # if we move left, in error
            if y+1 <= self.maxY and self.OccupancyMatrix [x, y+1] ==self.EMPTY:  
                # yes we can move
                self.right_moves[x, y, x, y+1] += self.prob_left_error

            else:
                # no we can't, stay stuck
                self.right_moves[x, y, x, y] += self.prob_left_error

            # if we move right, in error
            if y-1 >= 0 and self.OccupancyMatrix [x, y-1] ==self.EMPTY:
                # yes we can move
                self.right_moves[x, y, x, y-1] += self.prob_right_error
            else:
                # no we can't, stay stuck
                self.right_moves[x, y, x, y] += self.prob_right_error

            #print ('Transistion Array for Rightwards moves at : ' + str(x) +', ' + str(y))  #DEBUG
            #print (self.right_moves[x,y])      #DEBUG
        
        
        #Now LEFT moves
        # create and zero an array of all squares, for each square itself
        self.left_moves = np.zeros([self.maxX+1, self.maxY+1, self.maxX+1, self.maxY+1], dtype = float)

        for x, y in np.ndindex(self.OccupancyMatrix.shape):
            #current square is self.OccupancyMatrix[current_x,current_y]

            # if we move ahead, as commanded
            # if we are still within the game area and the ahead square is empty
            if x-1 >= 0 and self.OccupancyMatrix [x-1, y] == self.EMPTY: #ok because python evaluates 'and' lazily
                # yes we can move
                self.left_moves[x, y, x-1, y] += self.prob_ahead
            else:
            # no we can't, we're stuck
                self.left_moves[x, y, x, y] += self.prob_ahead

            # if we move left, in error
            if y-1 >= 0 and self.OccupancyMatrix [x, y-1] ==self.EMPTY:  
                # yes we can move
                self.left_moves[x, y, x, y-1] += self.prob_left_error

            else:
                # no we can't, stay stuck
                self.left_moves[x, y, x, y] += self.prob_left_error

            # if we move right, in error
            if y+1 <= self.maxY and self.OccupancyMatrix [x, y+1] ==self.EMPTY:
                # yes we can move
                self.left_moves[x, y, x, y+1] += self.prob_right_error
            else:
                # no we can't, stay stuck
                self.left_moves[x, y, x, y] += self.prob_right_error

            #print ('Transistion Array for Leftwards moves at : ' + str(x) +', ' + str(y))  #DEBUG
            #print (self.left_moves[x,y])      #DEBUG    

        #Now UP moves
        # create and zero an array of all squares, for each square itself
        self.up_moves = np.zeros([self.maxX+1, self.maxY+1, self.maxX+1, self.maxY+1], dtype = float)

        for x, y in np.ndindex(self.OccupancyMatrix.shape):
            #current square is self.OccupancyMatrix[current_x,current_y]

            # if we move ahead, as commanded
            # if we are still within the game area and the ahead square is empty
            if y+1 <= self.maxY and self.OccupancyMatrix [x, y+1] == self.EMPTY: #ok because python evaluates 'and' lazily
                # yes we can move
                self.up_moves[x, y, x, y+1] += self.prob_ahead
            else:
            # no we can't, we're stuck
                self.up_moves[x, y, x, y] += self.prob_ahead

            # if we move left, in error
            if x-1 >= 0 and self.OccupancyMatrix [x-1, y] ==self.EMPTY:  
                # yes we can move
                self.up_moves[x, y, x-1, y] += self.prob_left_error

            else:
                # no we can't, stay stuck
                self.up_moves[x, y, x, y] += self.prob_left_error

            # if we move right, in error
            if x+1 <= self.maxX and self.OccupancyMatrix [x+1, y] ==self.EMPTY:
                # yes we can move
                self.up_moves[x, y, x+1, y] += self.prob_right_error
            else:
                # no we can't, stay stuck
                self.up_moves[x, y, x, y] += self.prob_right_error

            #print ('Transistion Array for Upwards moves at : ' + str(x) +', ' + str(y))  #DEBUG
            #print (self.up_moves[x,y])      #DEBUG    




        #Now DOWN moves
        # create and zero an array of all squares, for each square itself
        self.down_moves = np.zeros([self.maxX+1, self.maxY+1, self.maxX+1, self.maxY+1], dtype = float)

        for x, y in np.ndindex(self.OccupancyMatrix.shape):
            #current square is self.OccupancyMatrix[current_x,current_y]

            # if we move ahead, as commanded
            # if we are still within the game area and the ahead square is empty
            if y-1 >= 0 and self.OccupancyMatrix [x, y-1] == self.EMPTY: #ok because python evaluates 'and' lazily
                # yes we can move
                self.down_moves[x, y, x, y-1] += self.prob_ahead
            else:
            # no we can't, we're stuck
                self.down_moves[x, y, x, y] += self.prob_ahead

            # if we move left, in error
            if x+1 <= self.maxX and self.OccupancyMatrix [x+1, y] ==self.EMPTY:  
                # yes we can move
                self.down_moves[x, y, x+1, y] += self.prob_left_error

            else:
                # no we can't, stay stuck
                self.down_moves[x, y, x, y] += self.prob_left_error

            # if we move right, in error
            if x-1 <= 0 and self.OccupancyMatrix [x-1, y] ==self.EMPTY:
                # yes we can move
                self.down_moves[x, y, x-1, y] += self.prob_right_error
            else:
                # no we can't, stay stuck
                self.down_moves[x, y, x, y] += self.prob_right_error   

            #print ('Transistion Array for Downwards moves at : ' + str(x) +', ' + str(y))  #DEBUG
            #print (self.down_moves[x,y])      #DEBUG    

        # flatten 2d subarrays to 1D for mdptoolbox
            right_moves_1D = np.empty([self.maxX+1,self.maxY+1, (self.maxX+1) * (self.maxY+1)], dtype = float)
            for x, y in np.ndindex(self.OccupancyMatrix.shape):
                #print ('2D Transistion Array for Rightwards moves at : ' + str(x) +', ' + str(y))  #DEBUG
                #print (self.right_moves[x,y])      #DEBUG
                right_moves_1D[x,y]= self.right_moves[x,y].flatten()


            left_moves_1D = np.empty([self.maxX+1,self.maxY+1, (self.maxX+1) * (self.maxY+1)], dtype = float)
            for x, y in np.ndindex(self.OccupancyMatrix.shape):
                left_moves_1D[x,y]= self.right_moves[x,y].flatten()

            up_moves_1D = np.empty([self.maxX+1,self.maxY+1, (self.maxX+1) * (self.maxY+1)], dtype = float)
            for x, y in np.ndindex(self.OccupancyMatrix.shape):
                up_moves_1D[x,y]= self.right_moves[x,y].flatten()

            down_moves_1D = np.empty([self.maxX+1,self.maxY+1, (self.maxX+1) * (self.maxY+1)], dtype = float)
            for x, y in np.ndindex(self.OccupancyMatrix.shape):
                down_moves_1D[x,y]= self.right_moves[x,y].flatten()    

        #flatten game areas from x, y indexed to linear array of transistion arrays, ready for mdptoolbox

            self.right_moves_mdp = np.empty([self.numSquares, self.numSquares], dtype= float)
            for x, y in np.ndindex(self.OccupancyMatrix.shape):
                i = x*(self.maxY+1)+y
                for j in range(self.numSquares):
                    self.right_moves_mdp[i,j] = right_moves_1D[x,y,j]
                #print ('1D Transistion Array for Rightwards moves at : ' + str(x) +', ' + str(y))  #DEBUG
                #print (right_moves_1D[x,y])      #DEBUG

            #print ('mdptoolbox Transistion Array for Rightwards moves:')  #DEBUG
            #print (self.right_moves_mdp)      #DEBUG

            self.left_moves_mdp = np.empty([self.numSquares, self.numSquares], dtype= float)
            for x, y in np.ndindex(self.OccupancyMatrix.shape):
                i = x*(self.maxY+1)+y
                for j in range(self.numSquares):
                    self.left_moves_mdp[i,j] = left_moves_1D[x,y,j]

            self.up_moves_mdp = np.empty([self.numSquares, self.numSquares], dtype= float)
            for x, y in np.ndindex(self.OccupancyMatrix.shape):
                i = x*(self.maxY+1)+y
                for j in range(self.numSquares):
                    self.up_moves_mdp[i,j] = up_moves_1D[x,y,j]

            self.down_moves_mdp = np.empty([self.numSquares, self.numSquares], dtype= float)
            for x, y in np.ndindex(self.OccupancyMatrix.shape):
                i = x*(self.maxY+1)+y
                for j in range(self.numSquares):
                    self.down_moves_mdp[i,j] = down_moves_1D[x,y,j]            

            print ('mdptoolbox Transistion Array for downwards moves:')  #DEBUG
            print (self.down_moves_mdp)      #DEBUG               

        sys.exit()

 