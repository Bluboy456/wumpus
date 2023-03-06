# config.py
#
# Configuration information for the Wumpus World. These are elements
# to play with as you develop your solution.
#
# Written by: Simon Parsons
# Last Modified: 25/08/20

# Number of games to be played to genetae statistics
number_of_games = 5

# Dimensions in terms of the numbers of rows and columns
worldLength = 10
worldBreadth = 8


# Features
numberOfWumpus = 1
numberOfPits = 3
numberOfGold = 1

# Control dynamism
#
# If dynamic is True, then the Wumpus will move.
dynamic = False

# Control observability --- NOT YET IMPLEMENTED
#
# If partialVisibility is True, Link will only see part of the
# environment.
partialVisibility = False
#
# The limits of visibility when visibility is partial
sideLimit = 1
forwardLimit = 5

# Control determinism
#
# If nonDeterministic is True, Link's action model will be
# nonDeterministic.
nonDeterministic = True
#
# If Link is nondeterministic, probability that they carry out the
# intended action:
directionProbability = 0.8

#General Guidance
maxBias = 0.5

#Local guidance flag

localGuidance = False


biasLeft = False
biasRight = False
biasUp = False
biasDown = False

# Control images
#
# If useImage is True, then we use images for Link, Wumpus and
# Gold. If it is False, then we use simple colored objects.
useImage = True
