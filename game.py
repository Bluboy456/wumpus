# game.py
#
# The top level loop that runs the game until Link wins or loses.
#
# run this using:
#
# python3 game.py
#
# Written by: Simon Parsons
# Last Modified: 25/08/20

from world import World
from link  import Link
from dungeon import Dungeon
import config
import utils
import time




# intialise recording statistics
gold_proportion = 0.0
win_proportion = 0.0
win_count = 0
gold_count = 0
av_gold_per_game = 0.0
total_num_moves = 0
av_moves_per_game = 0.0
number_pit_falls = 0
number_wumpus_eats = 0


#play a number of games and record results
game_no = config.number_of_games
while game_no > 0:
    game_no += -1
    # run a game
    gameWorld = World()
    player = Link(gameWorld)
    display = Dungeon(gameWorld)

    # set up Guidance Type
    # guidance = input('Would you like to help the Link (y/n)?\n')
    guidance = 'y'   #DEBUG
    if guidance == 'y':
        #adviceType = input('Do you want to give general or local advice? (g/l)\n')
        adviceType = 'l'  #DEBUG
        if adviceType == 'g':
            biasDirection = input('Which direction would you advise the Link to move in (n,ne,e,se,s,sw,w,nw? \n')
            config.biasUp = ('n'in biasDirection) 
            config.biasDown = ('s' in biasDirection)
            config.biasLeft = ('w' in biasDirection)
            config.biasRight = ('e' in biasDirection)

        elif adviceType == 'l':
              #Set a flag for local advice to be used in world.py
              config.localGuidance = True


        

    move_count = 0  
    while not(gameWorld.isEnded()):
        utils.printGameState(gameWorld)  #DEBUG
        if gameWorld.updateLink(player.makeMove()):  #returns True if some gold looted
            gold_count +=1
        gameWorld.updateWumpus()
        move_count += 1
        # Uncomment this for a printout of world state
        # utils.printGameState(gameWorld)
        display.update()
        time.sleep(1)  #comment out to speed up games for statistics
    
    if gameWorld.status == utils.State.WON:
            print("You won!")
            win_count +=1
    elif gameWorld.status == utils.State.PIT:
            print("You fell in pit and lost!")
            number_pit_falls += 1
    elif gameWorld.status == utils.State.WUMPUS: 
            print("You were caught by a Wumpus and lost!")
            number_wumpus_eats += 1
    total_num_moves = total_num_moves + move_count     

#calculate final statistics
win_proportion = win_count/config.number_of_games
gold_proportion = gold_count/config.number_of_games
av_moves_per_game = total_num_moves/config.number_of_games
pit_fall_proportion = number_pit_falls/config.number_of_games

print ('game area: ', config.worldLength, ' x ', config.worldBreadth)
print ('Number of gold: ', config.numberOfGold)
print ('Number of Wumpus: ', config.numberOfWumpus)
print ('Number of Pits: ', config.numberOfPits)
print( 'proportion of games won: ', "{:.2f}".format(win_proportion) )
print( 'average pots of gold looted per game: ', "{:.2f}".format(gold_proportion ))
print('proportion of games lost by pit falls:  ', "{:.2f}".format(pit_fall_proportion))
print( 'average number of moves per game: ', "{:.2f}".format(av_moves_per_game  ))



