from random import choice, randint


default_user_names = [
    'Jerry Lera',
    'Wardy Sanchy',
    'Carly Hingte',
    'Lase Risimm',
    'Eatrin Lenes',
    'Remy Guezal',
    'Michy Mithy',
    'Carlie Hughy',
    'Jamy Grison',
    'Jone Bailee',
    'Rosa Thallee',
    'Amed Phalley',
    'Rothy Theson',
    'Rahia Garce',
    'Heri Walker',
    'Pama Walking',
    'Inen Hillee',
    'Marie Howard',
    'Sica Pete',
    'Janie Grobarn',
    'Mesklou',
    'Tokiee',
    'Metha Zini',
    'Adenz',
    'Mauti',
    'Aehan',
    'Sharri',
    "A'Utwixtl",
    'Vorcia',
    "S'Strathua"
]  # courtesy of http://donjon.bin.sh/scifi/name/#space

# Development
remote_server_name = 'localhost'
remote_server_port = 9999

# Production
#remote_server_name = 'spacesnakes.com'
#remote_server_port = 62458

reserved_games = {
    'join_game_lobby': '9E06B364-1B03-4625-954A-9DA8F2EE0CEA'
}
user_name = choice(default_user_names) + str(randint(100, 999))