from networking.configuration import reserved_games
from networking.server import HOST, PORT
from networking.server.controllers.game import start_game
from networking.server.request_handler import UDPHandler
from networking.server.scheduled_tasks import debug_task, garbage_collection
from utilities.threading_helper import RepeatTask

import logging
import SocketServer


if __name__ == "__main__":
    # create reserved games
    for reserved_game in reserved_games:
        start_game(
            name=reserved_games[reserved_game],
            owner='reserved_game',
            map_name=''
        )

    # kick off scheduled tasks
    garbage_collection_thread = RepeatTask(20, garbage_collection)
    garbage_collection_thread.start()

    debug_thread = RepeatTask(10, debug_task)
    # debug_thread.start()

    # start the server
    server = SocketServer.UDPServer((HOST, PORT), UDPHandler)
    logging.info('Server listening on {host}:{port}'.format(host=HOST, port=str(PORT)))
    server.serve_forever()