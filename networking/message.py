from select import select

import cPickle
import socket


class Message():

    def __init__(self, message_type='DEFAULT_MESSAGE'):
        self.message_type = message_type


def enum(**enums):
    return type('Enum', (), enums)


def send_message(message, server, port, wait_for_response=True):
    # Create socket to send/receive from server.
    #   (SOCK_DGRAM is the socket type to use for UDP sockets)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_socket.sendto(cPickle.dumps(message), (server, port))

    if wait_for_response:
        server_socket.setblocking(0)

        ready = select([server_socket], [], [], 2)
        if ready[0]:
            received = server_socket.recv(4096)
            return cPickle.loads(received)

        raise Exception('Timeout occurred while waiting for a response from the server.')