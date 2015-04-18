from game import Game, GameSettings

import datetime
import time


#
# An example of how to create a new game as a client.
#

time_stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
game_name = 'Lobby ' + time_stamp


game_settings = GameSettings(
    server='localhost',
    server_port=9999,
    name=game_name,
    user_name='baerbradford'  # automatically joins as first player and game owner
)

game = Game(game_settings)


#
# How to get a list of games on a given server.
#

from networking.game import list_available_games

print list_available_games('localhost', 9999)


#
# How to join a game once you know the game name and server info. (using the game name from before)
#

from networking.game import join_game

game = join_game(game_name, 'localhost', 9999, 'user_2')

game = join_game(game_name, 'localhost', 9999, 'user_3')