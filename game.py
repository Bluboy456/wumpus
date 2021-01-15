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
number_of_games = 10

#play a number of games and record results
game_no = number_of_games
while game_no > 0:
    game_no += -1
    # run a game
    gameWorld = World()
    player = Link(gameWorld)
    display = Dungeon(gameWorld)
    move_count = 0  
    while not(gameWorld.isEnded()):
        if gameWorld.updateLink(player.makeMove()):  #returns True if some gold looted
            gold_count +=1
        gameWorld.updateWumpus()
        move_count += 1
        # Uncomment this for a printout of world state
        # utils.printGameState(gameWorld)
        display.update()
        #time.sleep(1)  #comment out to speed up games for statistics
    
    if gameWorld.status == utils.State.WON:
            print("You won!")
            win_count +=1
    else:
            print("You lost!")
    total_num_moves = total_num_moves + move_count     

#calculate final statistics
win_proportion = win_count/number_of_games
gold_proportion = gold_count/number_of_games
av_moves_per_game = total_num_moves/number_of_games

print ('game area: ', config.worldLength, ' x ', config.worldBreadth)
print ('Number of gold: ', config.numberOfPits)
print ('Number of Wumpus: ', config.numberOfWumpus)
print( 'proportion of games won: ', "{:.2f}".format(win_proportion) )
print( 'avearge pots of gold looted per game: ', "{:.2f}".format(gold_proportion ))
print( 'average number of moves per game: ', "{:.2f}".format(av_moves_per_game  ))



