from networking.server.database.active_game import ActiveGameDB
from networking.server.database.chat_message import ChatMessage
from networking.server.database.player import PlayerDB
from sqlite3 import connect, PARSE_DECLTYPES


class MemoryDatabase():

    def __init__(self):
        self.connection = connect(':memory:', check_same_thread=False, detect_types=PARSE_DECLTYPES)

        self.chat_message = ChatMessage(connection=self.connection)
        self.chat_message.build_table()

        self.active_game = ActiveGameDB(connection=self.connection)
        self.active_game.build_table()

        self.player = PlayerDB(connection=self.connection)
        self.player.build_table()