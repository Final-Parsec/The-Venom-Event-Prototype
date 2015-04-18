from networking.message import Message, send_message
from utilities.threading_helper import RepeatTask

import globals


class Game:

    def __init__(self, settings=None):
        if hasattr(globals, 'online_game') and globals.online_game is not None:
            globals.online_game.stop_all_threads()

        self.keep_alive_thread = None
        self.update_game_data_thread = None

        if settings:
            self.server = settings.server
            self.server_port = settings.server_port
            self.name = settings.name
            self.owner = settings.user_name
            self.map_name = settings.map_name
            self.status = 'lobby'

            message = Message(message_type='START_GAME')
            message.name = self.name
            message.owner = self.owner
            message.map_name = self.map_name

            send_message(message, self.server, self.server_port, wait_for_response=False)

            self.start_keep_alive_thread()
            self.start_update_game_data_thread()

    def get_players(self):
        """
        Returns an array of player names in game.
        """
        message = Message(message_type='LIST_GAME_PLAYERS')
        message.name = self.name

        return send_message(message, self.server, self.server_port)

    def get_new_messages(self, last_message_received):
        """
        Returns all messages for the game since the last poll.
        """
        message = Message(message_type='GET_GAME_MESSAGES')
        message.name = self.name
        message.last_received = last_message_received

        return send_message(message, self.server, self.server_port)

    def keep_alive(self):
        """
        Sends a keep alive message (AKA ping) to the server to prevent being idle and kicked.
        """
        from networking.configuration import user_name

        message = Message(message_type='PING')
        message.user_name = user_name

        send_message(message, self.server, self.server_port, wait_for_response=False)

    def set_status(self, new_status):
        message = Message(message_type='SET_GAME_STATUS')
        message.game_name = self.name
        message.new_status = new_status

        send_message(message, self.server, self.server_port, wait_for_response=False)

    def start_keep_alive_thread(self):
        self.keep_alive_thread = RepeatTask(3, self.keep_alive)
        self.keep_alive_thread.start()

    def start_update_game_data_thread(self):
        self.update_game_data_thread = RepeatTask(1, self.update_game_data)
        self.update_game_data_thread.start()

    def stop_all_threads(self):
        """
        Use this when leaving a game.
        """
        self.keep_alive_thread.stop()
        self.update_game_data_thread.stop()

    def update_game_data(self):
        """
        Updates game data from server.
        """
        message = Message(message_type='UPDATE_GAME_DATA')
        message.game_name = self.name

        game_data = send_message(message, self.server, self.server_port, wait_for_response=True)

        self.owner = game_data.owner
        self.map_name = game_data.map_name
        self.status = game_data.status


def join_game(game_name, server, server_port, user_name):
    message = Message(message_type='JOIN_GAME')
    message.game_name = game_name
    message.user_name = user_name

    message = send_message(message, server, server_port, wait_for_response=True)

    joined_game = Game()
    joined_game.server = server
    joined_game.server_port = server_port
    joined_game.name = game_name
    joined_game.map_name = message['map_name']

    joined_game.start_keep_alive_thread()
    joined_game.start_update_game_data_thread()

    return joined_game


def leave_game(game_name, server, server_port, user_name):
    if hasattr(globals, 'online_game') and globals.online_game:
        globals.online_game.stop_all_threads()

    message = Message(message_type='LEAVE_GAME')
    message.game_name = game_name
    message.user_name = user_name

    send_message(message, server, server_port, wait_for_response=False)


def list_available_games(server, server_port):
    message = Message(
        message_type='LIST_AVAILABLE_GAMES'
    )

    available_games = send_message(message, server, server_port)

    return available_games


def chat_message(chat_message, server, server_port, user_name, game_name):
    if not chat_message:
        return

    message = Message(message_type='CHAT_MESSAGE')
    message.chat_message = chat_message
    message.user_name = user_name
    message.name = game_name

    return send_message(message, server, server_port, wait_for_response=False)


class GameSettings:

    def __init__(self, server, server_port, name, user_name, map_name):
        self.server = server
        self.server_port = server_port
        self.name = name
        self.user_name = user_name
        self.map_name = map_name
