# Global packages/builtins
import socket

# Package modules
from globals import dlogger
from lan.connection import Connection


class ClientHandler(Connection):
    """
    ClientHandler is a class that handles the connection to clients.
    """

    def __init__(self, port, socket_accept_delay=0.01):
        """
        Initialize the ClientHandler.
        """
        super().__init__(port=port)
        self._clients = []
        self._socket_accept_delay = socket_accept_delay

        self._init_socket()
        self._clients = []
    
    def _init_socket(self):
        """
        Initialize the socket.
        """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(('', self._port))
        self._socket.listen(5)
        self._socket.settimeout(self._socket_accept_delay)

    def accept_clients(self):
        """
        Accept clients and add them to the list of clients.
        Returns:
            int: the number of clients that were added.
        """
        num_clients = 0
        try:
            while True:
                client_sock, address = self._socket.accept()
                client = Connection(ip=address[0], port=address[1], socket=client_sock)
                self._clients.append(client)
                self._clients[-1].settimeout(0.01)
                num_clients += 1
        except socket.timeout:
            pass
        return num_clients

    def receive_tcp_all_clients(self) -> bool:
        """
        Receive all messages from all clients.
        Stores all messages in a list attribute.
        Retrieve the messages by calling the get_msgs() method.
        Returns:
            bool: True if a message was received, False otherwise.
        """
        len_before = len(self._recvd_msgs)
        dlogger.log_debug(f'Receiving messages from all clients.')
        for client in self._clients:
            client.receive_tcp_all()
            # Add each message to the list of messages
            for msg in client.get_recvd_messages():
                self._recvd_msgs.append(msg)
            client.clear_recvd_messages()
        return len(self._recvd_msgs) > len_before


    def send_tcp_all_clients(self, msg: str):
        '''
        Send a message to all connected clients
        Args:
            msg: the message to send
        '''
        dlogger.log_debug(f'Sending {msg} to all clients.')
        for client in self._clients:
            client.dynamic_send(msg)


    def has_clients(self):
        """
        Return True if there are clients connected, False otherwise.
        """
        return len(self._clients) > 0