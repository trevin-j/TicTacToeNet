'''
An abstract class for a multiplayer game.
Note: Many methods implemented will take time to execute.
This multiplayer style is only meant for turn-based cli games.
In the future, I might work on adding support for multithreading.
'''

import time

from lan.connection import Connection
from lan.lan import check_lan_servers
from lan.broadcast_responder import BroadcastResponder
from lan.client_handler import ClientHandler

from globals import dlogger

class MultiplayerGame:
    LOCAL = 0
    LAN = 1

    def search_for_hosts(self) -> list:
        '''
        Search for existing games.
        Returns a list of Connection objects. One for each host.
        '''
        if not self._port:
            raise ValueError('Port not set.')
        return check_lan_servers(self._port)

    def connect_to_host(self, host: Connection) -> None:
        '''
        Connect to an existing game.
        '''
        self._connection = host
        self._connection.tcp_connect()
        self._host = False

    def create_host(self) -> None:
        '''
        Create a new game.
        '''
        self._connection = ClientHandler(self._port)
        self._broadcast_responder = BroadcastResponder(self._port)
        self._host = True

    def wait_and_connect_client(self) -> None:
        '''
        Wait for a client to connect.
        '''
        while not self._connection.has_clients():
            self._broadcast_responder.respond_to_broadcast('ping')
            self._connection.accept_clients()

    def send_to_peer(self, msg: str) -> None:
        '''
        Send a message to the peer.
        '''
        # if self._connection.is_connected():
        #     dlogger.log_info('Client still connected. Sending message...')
        # else:
        #     dlogger.log_info('Client disconnected. Expect a crash.')

        if not self._host:
            self._connection.dynamic_send(msg)
        else:
            self._connection.send_tcp_all_clients(msg)
    

    def receive_from_peer(self) -> str:
        '''
        Receive a message from the peer.
        '''
        # if self._connection.is_connected():
        #     dlogger.log_info('Client still connected. Receiving message...')
        # else:
        #     dlogger.log_info('Client disconnected. Expect a crash.')

        if not self._host:
            while not self._connection.dynamic_receive():
                time.sleep(0.1)
        else:
            while not self._connection.receive_tcp_all_clients():
                time.sleep(0.1)
        msgs = self._connection.get_recvd_messages()
        self._connection.clear_recvd_messages()
        return msgs[0]