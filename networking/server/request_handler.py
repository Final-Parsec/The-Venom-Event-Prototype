from datetime import datetime
from time import time

import cPickle
import logging
import SocketServer


# Dictionary that maps message types to the function which handles it.
message_handlers = {}


def add_message_type_handler(message_type, function_to_call):
    message_handlers[message_type] = function_to_call


def message_type_handler(message_type):
    def decorator(function_to_call):
        add_message_type_handler(message_type, function_to_call)
        return function_to_call
    return decorator


class UDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            logging.info('MESSAGE RECEIVED from {ip} at {time_stamp}'.format(
                ip=self.client_address[0],
                time_stamp=datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')
            ))

            data = self.request[0].strip()
            message = cPickle.loads(data).__dict__
            message_type = message['message_type']
            del message['message_type']  # This parameter is only needed by the UDPHandler.
            logging.info('Message type: {type}'.format(type=message_type))

            if message_type in message_handlers:
                data = message_handlers[message_type](**message)
            else:
                logging.warning('Unknown message type.')

            # Reply if there is any data to send back to the client.
            if data:
                socket = self.request[1]
                socket.sendto(data, self.client_address)
        except Exception:
            logging.exception('ERROR OCCURRED - {time_stamp}'.format(
                time_stamp=datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')
            ))