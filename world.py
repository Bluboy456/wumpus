# world.py
#
# A file that represents the Wumpus World, keeping track of the
# position of all the objects: pits, Wumpus, gold, and the agent, and
# moving them when necessary.
#
# Written by: Simon Parsons
# Last Modified: 25/08/20
#
# Modified by: Stuart Jessup
# Last Modified 28/12/20
# Now always places itemsin a vacant square

import random
import config
import utils
from utils import Pose
from utils import Directions
from utils import State

class World():

    def __init__(self):

        # Import boundaries of the world. because we index from 0,
        # these are one less than the number of rows and columns.
        self.maxX = config.worldLength - 1
        self.maxY = config.worldBreadth - 1

        self.occupied_locations = []          #list of locations that already have something there
    
        
        # Wumpus
        self.wLoc = []
        for i in range(config.numberOfWumpus):
            while True:
                vacant = True   #MODIFIED SJ - moved inside loop to fix infinite loop SJ
                trial_pose = utils.pickRandomPose(self.maxX, self.maxY)  
                for pose in self.occupied_locations:
                    if pose.x == trial_pose.x and pose.y == trial_pose.y:    #location is already taken
                        vacant = False

                if vacant == True:
                    self.wLoc.append(trial_pose)
                    self.occupied_locations.append(trial_pose)
                    break


    
        # Gold
        self.gLoc = []
        for i in range(config.numberOfGold):
            while True:
                vacant = True   #MODIFIED SJ - moved inside loop to fix infinite loop SJ
                trial_pose = utils.pickRandomPose(self.maxX, self.maxY)  
                vacant = True
                for pose in self.occupied_locations:
                    if pose.x == trial_pose.x and pose.y == trial_pose.y:    #location is already taken
                        vacant = False

                if vacant == True:
                    self.gLoc.append(trial_pose)
                    self.occupied_locations.append(trial_pose)
                    break

        # Pits
        self.pLoc = []
        for i in range(config.numberOfPits):
            while True:
                trial_pose = utils.pickRandomPose(self.maxX, self.maxY) 
                vacant = True 
                for pose in self.occupied_locations:
                    if pose.x == trial_pose.x and pose.y == trial_pose.y:    #location is already taken
                        vacant = False

                if vacant == True:
                    self.pLoc.append(trial_pose)
                    self.occupied_locations.append(trial_pose)
                    break

         # Link

        while True:
            trial_pose = utils.pickRandomPose(self.maxX, self.maxY)
            vacant = True 
            for pose in self.occupied_locations:
                if pose.x == trial_pose.x and pose.y == trial_pose.y:    #location is already taken
                    vacant = False

            if vacant == True:
                self.lLoc = trial_pose
                #print('Initial Link Pose')  #DEBUG
                #print(self.lLoc.x, self.lLoc.y)  #DEBUG
                self.occupied_locations.append(trial_pose)
                break


        # Game state
        self.status = State.PLAY

        # Did Link just successfully loot some gold?
        self.looted = False
        
    #
    # Access Methods
    #
    # These are the functions that should be used by Link to access
    # information about the world.

    #What is the breadth of the world?
    def getMaxX(self):
        return self.maxX

    def getMaxY(self):
        return self.maxY

    # Where is/are the Wumpus?
    def getWumpusLocation(self):
        return self.wLoc

    # Where is Link?
    def getLinkLocation(self):
        return self.lLoc

    # Where is the Gold?
    def getGoldLocation(self):
        return self.gLoc

    # Where are the Pits?
    def getPitsLocation(self):
        return self.pLoc

    # Did we just loot some gold?
    def justLooted(self):
        return self.looted

    # What is the current game state?
    def getGameState(self):
        return self.status

    # Does Link feel the wind?
    def linkWindy(self):
        return self.isWindy(self.lLoc)

    # Does Link smell the Wumpus?
    def linkSmelly(self):
        #print('Link location ')  #DEBUG
        #print(self.lLoc.x, self.lLoc.y) #DEBUG
        return self.isSmelly(self.lLoc)

    # Does Link see the glitter?
    def linkGlitter(self):
        return self.isGlitter(self.lLoc)
 
    #
    # Methods
    #
    # These are the functions that are used to update and report on
    # world information.

    def isEnded(self):
        dead = False
        won = False
        # Has Link met the Wumpus?
        for i in range(len(self.wLoc)):
            if utils.sameLocation(self.lLoc, self.wLoc[i]):
                print("Oops! Met the Wumpus")
                dead = True
                self.status = State.WUMPUS
                
        # Did Link fall in a Pit?
        for i in range(len(self.pLoc)):
            if utils.sameLocation(self.lLoc, self.pLoc[i]):
                print("Arghhhhh! Fell in a pit")
                dead = True
                self.status = State.PIT

        # Did Link loot all the gold?
        if len(self.gLoc) == 0:
            won = True
            self.status = State.WON
            
        if self.status == State.PIT or self.status == State.WUMPUS or self.status == State.WON:
            print("Game Over!")
            return True
        else:
            return False
            
    # Implements the move chosen by Link
    # config definitions
    # right = SOUTH, left = NORTH, up = EAST, down = WEST
    # Updated SJ to return gold status - True if gold looted
    def updateLink(self, direction):
        # Set the looted flag to False
        self.looted = False

        # Human overide to move link if adjacent to occupied square
        # if True:  #DEBUG
        if self.linkWindy() and config.localGuidance == True:
            print('Help, I am next to a pit, please move me away')
            print ('Enter the direction to move me(l/r/u/d)')
            safe_direction = input()
            if safe_direction == 'd': direction = Directions.NORTH
            if safe_direction == 'u': direction = Directions.SOUTH
            if safe_direction == 'r': direction = Directions.EAST
            if safe_direction == 'l': direction = Directions.WEST
               
        elif self.linkSmelly() and config.localGuidance == True:
            print('Help, I am next to a Wumpus, please move me away')
            print ('Enter the direction to move me (l/r/u/d)')
            safe_direction = input()
            if safe_direction == 'l': direction == Directions.WEST
            if safe_direction == 'r': direction == Directions.EAST
            if safe_direction == 'u': direction == Directions.NORTH
            if safe_direction == 'd': direction == Directions.SOUTH    

        elif self.linkGlitter() and config.localGuidance == True:
            print('I am next to gold, please help me loot it')
            print ('Enter the direction to move me (l/r/u/d)')
            safe_direction = input()
            if safe_direction == 'l': direction == Directions.WEST
            if safe_direction == 'r': direction == Directions.EAST
            if safe_direction == 'u': direction == Directions.NORTH
            if safe_direction == 'd': direction == Directions.SOUTH    
            
        
        # If not next to anything direction is probablitic based on Value Interation
        else: direction = self.probabilisticMotion(direction)





        if direction == Directions.NORTH:
            if self.lLoc.y < self.maxY:
                self.lLoc.y = self.lLoc.y + 1
            
        if direction == Directions.SOUTH:
            if self.lLoc.y > 0:
                self.lLoc.y = self.lLoc.y - 1
                
        if direction == Directions.EAST:
            if self.lLoc.x < self.maxX:
                self.lLoc.x = self.lLoc.x + 1
                
        if direction == Directions.WEST:
            if self.lLoc.x > 0:
                self.lLoc.x = self.lLoc.x - 1

        # Did Link just loot some gold?
        match = False
        gold = False
        index = 0
        for i in range(len(self.gLoc)):
            if utils.sameLocation(self.lLoc, self.gLoc[i]):
                match = True
                gold = True
                index = i
                self.looted = True
                print("Gold, yeah!")

        # Assumes that golds have different locations. Or, that only
        # one gold can be picked up in a given turn.
        if match:
            self.gLoc.pop(index)

        if gold:
            return True  
        else:
            return False

    # Implement nondeterministic motion, if appropriate.
    def probabilisticMotion(self, direction):
        if config.nonDeterministic:
            dice = random.random()
            if dice < config.directionProbability:
                return direction
            else:
                return self.sideMove(direction)
        else:
            return direction
        
    # Move at 90 degrees to the original direction.
    def sideMove(self, direction):
        # Do we head left or right of the intended direction?
        dice =  random.random()
        if dice > 0.5:
            left = True
        else:
            left = False
        if direction == Directions.NORTH:
            if left:
                return Directions.WEST
            else:
                return Directions.EAST

        if direction == Directions.SOUTH:
            if left:
                return Directions.EAST
            else:
                return Directions.WEST

        if direction == Directions.WEST:
            if left:
                return Directions.SOUTH
            else:
                return Directions.NORTH

        if direction == Directions.EAST:
            if left:
                return Directions.NORTH
            else:
                return Directions.SOUTH
            
    # Move the Wumpus if that is appropriate
    #
    # TODO - stop Wumpus moving over pits
    #
    def updateWumpus(self):
        if config.dynamic:
            #save Wumpus location before any move
            
            # Head towards Link
            target = self.lLoc
            for i in range(len(self.wLoc)):
                wumpusInitial = self.wLoc[i]
                # If same x-coordinate, move in the y direction
                if self.wLoc[i].x == target.x:
                    self.wLoc[i].y = self.reduceDifference(self.wLoc[i].y, target.y)        
                # If same y-coordinate, move in the x direction
                elif self.wLoc[i].y == target.y:
                    self.wLoc[i].x = self.reduceDifference(self.wLoc[i].x, target.x)        
                # If x and y both differ, approximate a diagonal
                # approach by randomising between moving in the x and
                # y direction.
                else:
                    dice = random.random()
                    if dice > 0.5:
                        self.wLoc[i].y = self.reduceDifference(self.wLoc[i].y, target.y)        
                    else:
                        self.wLoc[i].x = self.reduceDifference(self.wLoc[i].x, target.x)     
                # Check whether Wumpus would be in a pit, if so don't move
                if self.isAjacent(self.pLoc, self.wLoc[i]):
                    self.wLoc[i] = wumpusInitial

    # Move value towards target.
    def reduceDifference(self, value, target):
        if value < target:
            if random.random() < config.wumpusSpeed:  #control average speed of Wumpus
                return value+1
            else:
                return value
        elif value > target:
            if random.random() < config.wumpusSpeed:
                return value-1
            else:
                return value
        else:
            return value

    # Is the given location smelly?
    #
    # A location is smelly if it is next to the Wumpus
    def isSmelly(self, location):
        if self.isAjacent(self.wLoc, location): #MODIFIED SJ - wloc to wLoc
            return True
        else:
            return False

    # Is the given location windy? 
    def isWindy(self, location):
        if self.isAjacent(self.pLoc, location): #MODIFIED SJ - ploc to pLoc
            return True
        else:
            return False

     # Does the given location glitter? 
    def isGlitter(self, location):
        if self.isAjacent(self.gLoc, location): #MODIFIED SJ - gloc to gLoc
            return True
        else:
            return False
        
    # Is the location loc next to any of the locations in locList.
    #
    # To be adjacent in this sense, you either have to be at the same
    # x coordinate and have a y coordinate that differs by 1, or in
    # the same y coordinate and have an x coordinate that differs by
    # one.
    def isAjacent(self,locList, loc):
        for aloc in locList:
            #print ('link:')  #DEBUG
            #print (loc.x, loc.y)   #DEBUG
            #print ('thing')  #DEBUG
            #print (locList[0].x, locList[0].y)   #DEBUG
            # Ajacency holds if it holds for any location in locList.
            if aloc.x == loc.x:
                if aloc.y == loc.y + 1 or aloc.y == loc.y - 1:
                    return True
            elif aloc.y == loc.y:
                if aloc.x == loc.x + 1 or aloc.x == loc.x - 1:
                    return True
        return False
            
            
