from networking.configuration import remote_server_name, remote_server_port, user_name
from networking.message import Message, send_message


class PlayerNetworking():
    def __init__(self):
        pass

    def set_player_ready_status(self, button):
        """
        For client side use. Calls server and updates players ready status.

        ready parameter is a boolean
        """
        self.__init__()

        ready = button.is_pressed
        message = Message(message_type='SET_READY_STATUS')
        message.user_name = user_name
        message.ready = ready

        return send_message(message, remote_server_name, remote_server_port, wait_for_response=False)