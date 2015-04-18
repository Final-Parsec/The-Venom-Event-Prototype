from networking.server import memory_database
from networking.server.request_handler import message_type_handler

import cPickle
import logging


@message_type_handler('LIST_AVAILABLE_GAMES')
def list_available_games(pickled_response=True):
    available_games = memory_database.active_game.list_available_games()

    logging.debug('All active games:')
    for active_game in available_games:
        logging.debug('\t{game_name}'.format(
            game_name=active_game
        ))

    return cPickle.dumps(available_games) if pickled_response else available_games


@message_type_handler('SET_GAME_STATUS')
def set_game_status(game_name, new_status):
    memory_database.active_game.set_status(game_name, new_status)


@message_type_handler('START_GAME')
def start_game(name, owner, map_name):
    if not memory_database.player.exists(owner) and owner != 'reserved_game':
        memory_database.player.create(owner)

    memory_database.active_game.create(game_name=name, owner=owner, map_name=map_name)

    memory_database.player.join_game(user_name=owner, game_name=name)

    logging.debug('New game started: ' + name)


@message_type_handler('UPDATE_GAME_DATA')
def update_game_data(game_name):
    active_game = memory_database.active_game.get_active_game(game_name)
    return cPickle.dumps(active_game)