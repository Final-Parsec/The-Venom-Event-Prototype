class ChatMessage():

    def __init__(self, connection):
        self.connection = connection

    def build_table(self):
        #  Create chat_message table.
        self.connection.cursor().execute('''
            create table chat_message (
                id integer primary key autoincrement,
                game_name text,
                user_name text,
                chat_message text)
        ''')

        self.connection.commit()

    def create(self, game_name, user_name, chat_message):
        query = 'insert into chat_message (game_name, user_name, chat_message)'
        query += ' values (:game_name, :user_name, :chat_message)'

        self.connection.cursor().execute(query, {
            'chat_message': chat_message,
            'game_name': game_name,
            'user_name': user_name
        })

        self.connection.commit()

    def get(self, game_name, last_received):
        cursor = self.connection.cursor()
        cursor.execute('select * from chat_message where game_name=:game_name and id > :last_received', {
            'game_name': game_name,
            'last_received': int(last_received)
        })

        return cursor.fetchall()