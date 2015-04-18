from datetime import datetime
from networking.server import memory_database
from networking.server.controllers.game import list_available_games
from networking.server.controllers.player import in_game
from threading import Timer
from time import time

import logging


def garbage_collection():
    """
    Runs on a schedule performing garbage collection of idle players and empty games.
    """

    logging.debug('Garbage Collection Run: ' + datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S'))

    memory_database.player.kick_idle_players()

    for active_game in list_available_games(pickled_response=False):
        original_owner = memory_database.active_game.get_owner(game_name=active_game)
        current_players = in_game(name=active_game, pickled_response=False)

        if len(current_players) < 1:
            # Delete empty games.
            memory_database.active_game.delete(game_name=active_game)
        elif 'HOST: ' + original_owner not in current_players:
            # Reassign owner if original owner was kicked.
            memory_database.active_game.set_owner(game_name=active_game, new_owner=current_players[0].user_name)


# temporary debugging for whatever you please
def debug_task():

    print 'game table dump'
    query = 'select * from active_game'

    for row in memory_database.active_game.connection.cursor().execute(query):
        print row

    print '-----\n'