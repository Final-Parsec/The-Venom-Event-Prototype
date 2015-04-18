from networking.server import memory_database
from networking.server.request_handler import message_type_handler

import cPickle
import logging


@message_type_handler('LIST_GAME_PLAYERS')
def in_game(name, pickled_response=True):
    players = []
    logging.debug('Players in "{game_name}":'.format(game_name=name))
    for player in memory_database.player.in_game(game_name=name):
        if player == memory_database.active_game.get_owner(game_name=name):
            player = 'HOST: {player_name}'.format(
                player_name=player
            )

        players.append(player)
        logging.debug(player)

    return cPickle.dumps(players) if pickled_response else players


@message_type_handler('JOIN_GAME')
def join_game(game_name, user_name):
    logging.debug('{user} requested to join {game_name}'.format(
        user=user_name,
        game_name=game_name
    ))

    if not memory_database.player.exists(user_name):
        memory_database.player.create(user_name)

    memory_database.player.join_game(game_name=game_name, user_name=user_name)

    logging.debug('Players in {game_name}:'.format(
        game_name=game_name
    ))
    for player in memory_database.player.in_game(game_name):
        logging.debug('\t{player_name}'.format(
            player_name=player
        ))

    return cPickle.dumps({
        'map_name': memory_database.active_game.get_map_name(game_name)
    })


@message_type_handler('LEAVE_GAME')
def leave_game(game_name, user_name):
    logging.debug('{user} requested to leave {game_name}'.format(
        game_name=game_name,
        user=user_name
    ))

    memory_database.player.leave_game(user_name=user_name)

    for player in memory_database.player.in_game(game_name):
        logging.debug('\t{player_name}'.format(
            player_name=player
        ))


@message_type_handler('PING')
def ping(user_name):
    memory_database.player.ping(user_name=user_name)


@message_type_handler('SET_READY_STATUS')
def set_ready_status(user_name, ready):
    memory_database.player.set_ready_status(user_name, ready)