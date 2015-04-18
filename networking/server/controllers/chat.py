from networking.server import memory_database
from networking.server.request_handler import message_type_handler

import cPickle
import logging


@message_type_handler('GET_GAME_MESSAGES')
def get_messages(name, last_received):
    messages = []
    computed_last_received = 0
    logging.debug('Messages:')
    for message in memory_database.chat_message.get(game_name=name, last_received=last_received):
        messages.append('{user_name}: {message}'.format(
            message=message[3],
            user_name=message[2]
        ))
        computed_last_received = message[0] if message[0] > last_received else last_received

    return cPickle.dumps({
        'last_received': computed_last_received,
        'messages': messages
    })


@message_type_handler('CHAT_MESSAGE')
def send_chat_message(name, user_name, chat_message):
    logging.debug('{user} sent {chat_message} to game channel {game_name}'.format(
        chat_message=chat_message,
        game_name=name,
        user=user_name
    ))

    memory_database.chat_message.create(
        game_name=name,
        user_name=user_name,
        chat_message=chat_message
    )

    logging.debug(memory_database.chat_message.get(game_name=name, last_received=0))