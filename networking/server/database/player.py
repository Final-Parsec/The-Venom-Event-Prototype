from datetime import datetime, timedelta


class Player():
    """
    Representation of player as stored in the in-memory database (a single row from the player table).
    """

    def __init__(self, user_name, last_ping, in_game=None, ready=False):
        self.user_name = user_name
        self.last_ping = last_ping
        self.in_game = None if not in_game or in_game == '' else in_game
        self.ready = False if not ready else True


class PlayerDB():

    def __init__(self, connection):
        self.connection = connection

    def build_table(self):
        self.connection.cursor().execute('''
            create table player (
                user_name text not null primary key,
                in_game text null,
                last_ping text not null,
                ready boolean null)
        ''')

        self.connection.commit()

    def create(self, user_name):
        query = 'insert into player (user_name, last_ping)'
        query += ' values (:user_name, :last_ping)'

        self.connection.cursor().execute(query, {
            'last_ping': datetime.now(),
            'user_name': user_name
        })

        self.connection.commit()

    def exists(self, user_name):
        query = 'select count(*) from player where user_name = :user_name'

        cursor = self.connection.cursor()

        cursor.execute(query, {
            'user_name': user_name
        })
        count = cursor.fetchone()[0]

        return count > 0

    def in_game(self, game_name):
        """ Returns a list of players in a given game. """
        query = 'select user_name, last_ping, ready from player where in_game = :game_name'

        players_in_game = []

        cursor = self.connection.cursor()
        cursor.execute(query, {'game_name': game_name})
        for result in cursor.fetchall():
            players_in_game.append(Player(
                user_name=result[0],
                last_ping=result[1],
                ready=result[2],
                in_game=game_name
            ))

        return players_in_game

    def join_game(self, user_name, game_name):
        query = 'update player set in_game = :game_name where user_name = :user_name'

        self.connection.cursor().execute(query, {
            'user_name': user_name,
            'game_name': game_name
        })

        self.connection.commit()

    def kick_idle_players(self):
        query = 'update player set in_game = null where user_name != :reserved_game'
        query += ' and last_ping < :timeout_threshold'

        cursor = self.connection.cursor()

        cursor.execute(query, {
            'reserved_game': 'reserved_game',
            'timeout_threshold': datetime.now() - timedelta(seconds=10)
        })

        self.connection.commit()

    def leave_game(self, user_name):
        query = 'update player set in_game = null where user_name = :user_name'

        self.connection.cursor().execute(query, {
            'user_name': user_name
        })

        self.connection.commit()

    def ping(self, user_name):
        query = 'update player set last_ping = :last_ping where user_name = :user_name'

        self.connection.cursor().execute(query, {
            'last_ping': datetime.now(),
            'user_name': user_name
        })

        self.connection.commit()

    def set_ready_status(self, user_name, ready):
        query = 'update player set ready = :ready where user_name = :user_name'

        self.connection.cursor().execute(query, {
            'ready': ready,
            'user_name': user_name
        })