class ActiveGame():
    """
    Representation of game as stored in the in-memory database (a single row from the active game table).
    """
    def __init__(self, game_name, owner, map_name, status):
        self.game_name = game_name
        self.owner = owner
        self.map_name = map_name
        self.status = status


class ActiveGameDB():
    def __init__(self, connection):
        self.connection = connection

    def build_table(self):
        #  Create active_game table.
        self.connection.cursor().execute('''create table active_game (
                                                game_name text primary key,
                                                owner text,
                                                map_name text,
                                                status text
                                            )''')

        self.connection.commit()

    def create(self, game_name, owner, map_name):
        query = 'insert into active_game values (:game_name, :owner, :map_name, :status)'

        self.connection.cursor().execute(query, {
            'game_name': game_name,
            'owner': owner,
            'map_name': map_name,
            'status': 'lobby'
        })

        self.connection.commit()

    def delete(self, game_name):
        query = 'delete from active_game where game_name=:game_name'

        self.connection.cursor().execute(query, {
            'game_name': game_name
        })

        self.connection.commit()

    def get_active_game(self, game_name):
        query = 'select game_name, owner, map_name, status from active_game where game_name = :game_name'

        cursor = self.connection.cursor()
        cursor.execute(query, {'game_name': game_name})
        db_record = cursor.fetchone()
        return ActiveGame(
            game_name=db_record[0],
            owner=db_record[1],
            map_name=db_record[2],
            status=db_record[3]
        )

    # todo: remove this. user will get this information from get_game
    def get_map_name(self, game_name):
        query = 'select map_name from active_game where game_name = :game_name'

        cursor = self.connection.cursor()
        cursor.execute(query, {
            'game_name': game_name
        })

        return cursor.fetchone()[0]

    def get_owner(self, game_name):
        query = 'select owner from active_game where game_name = :game_name'

        cursor = self.connection.cursor()
        cursor.execute(query, {
            'game_name': game_name
        })

        return cursor.fetchone()[0]

    def list_available_games(self):
        query = "select game_name from active_game where owner != 'reserved_game'"

        active_games = []

        for active_game in self.connection.cursor().execute(query):
            active_games.append(active_game[0])

        return active_games

    def set_owner(self, game_name, new_owner):
        query = 'update active_game set owner = :new_owner where game_name=:game_name'

        self.connection.cursor().execute(query, {
            'game_name': game_name,
            'new_owner': new_owner
        })

        self.connection.commit()

    def set_status(self, game_name, status):
        query = 'update active_game set status = :status where game_name = :game_name'

        self.connection.cursor().execute(query, {
            'game_name': game_name,
            'status': status
        })

        self.conneciton.commit()