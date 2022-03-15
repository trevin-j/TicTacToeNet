# Global packages/builtins
import socket
import time

# Package modules
from globals import dlogger
from lan.connection import Connection

class BroadcastResponder(Connection):
    def __init__(self, port):
        '''
        Creates a Connection which holds the socket that will receive broadcast messages.
        This is used to respond to broadcast messages and tell the sender that the server is available.
        Args:
            port: The port to listen on.
        Returns:
            A Connection object.
        '''
        dlogger.log_info('Creating socket to receive UDP broadcasts on port ' + str(port))

        super().__init__(port=port)

        self.setup_br_socket()
        self.setup_sender_socket()

        # Attribute _recent_request_addrs holds the addresses of recently received broadcast messages.
        # If a broadcast message is received, the address is added to this list.
        # If a broadcast message is received from an address that is already in this list,
        # the message is ignored.
        # This is to prevent the server from responding to the same broadcast message multiple times.
        # After a certain amount of time, the address is removed from this list.
        self._recent_request_addrs = []

        self._recent_request_limit = 1.5

        

    def setup_br_socket(self):
        # Create a UDP socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dlogger.log_info('Socket created.')

        # Set the option to allow broadcast
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        dlogger.log_info('Broadcast socket set.')

        # Bind to the port
        self._socket.bind(('', self._port))
        dlogger.log_info('Broadcast socket bound to port ' + str(self._port))

        # Set timeout to be very very small
        self._socket.settimeout(0.01)

    
    def setup_sender_socket(self):
        '''
        Creates the sending socket that responds to broadcast messages
        '''
        # Create a UDP socket
        self._sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dlogger.log_info('Socket created.')

        # Set the option to allow broadcast
        self._sender_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        dlogger.log_info('Broadcast socket set.')


    def respond_to_broadcast(self, message='') -> bool:
        '''
        Listens for a very short period of time for a broadcast message.
        If a broadcast message is received, the message is sent back to the sender.
        First message structure: 'PYMULT_SERVER_RESPONSE(1--)'
        The second message contains a message the number of bytes in length as shown in the first message.
        The response message is sent on port + 1 to prevent conjestion.
        Args:
            message: The message to send back to the sender.
        Returns:
            True if a message was received, False otherwise.
        '''
        dlogger.log_debug('Listening for broadcast on port ' + str(self._port))

        # Briefly listen for a broadcast message.
        try:
            self._update_recent_request_addrs()
            msg, addr = self._socket.recvfrom(16)  # The broadcast message SHOULD contain exactly 16 bytes.

            # Make sure the message is not on the list of recently received messages.
            self._check_recent_request_addrs(addr)

            dlogger.log_info('Received packet from ' + str(addr))
            dlogger.log_info('Message: ' + str(msg))

            ip = addr[0]

            # In order for the broadcast to be valid, the first message must be 'PYMULT_BROADCAST'
            if msg != b'PYMULT_BROADCAST':
                dlogger.log_warning('Invalid broadcast message received. Ignoring.')
                return False

            dlogger.log_info('Sending response to broadcast.')
            # Send both messages back to the sender on the port + 1.
            identifier = f'PYMULT_SERVER_RESPONSE({len(message):<3})'
            fullmsg = identifier + message
            self._sender_socket.sendto(identifier.encode('utf-8'), (ip, self._port + 1))
            self._sender_socket.sendto(message.encode('utf-8'), (ip, self._port + 1))
            dlogger.log_info(f'Sent {fullmsg} as response to broadcast.')

            return True
        except socket.timeout:
            dlogger.log_debug('No broadcast message received.')
            return False
        except RecentRequestAddr:
            dlogger.log_info('Broadcast message from recently received address. Ignoring.')
            return False


    def _check_recent_request_addrs(self, addr):
        '''
        Checks if the address has recently sent a request.
        Removes any addresses that have not been sent a request for a certain amount of time.
        If it hasn't sent a request, the address is added to the list.
        If it has sent a request, the function raises RecentRequestAddr exception.
        Args:
            addr: The address to check.
        '''
        # Remove any addresses that have not been sent a request for a certain amount of time.
        for i, addr_ in enumerate(self._recent_request_addrs):
            if time.time() - addr_[1] > self._recent_request_limit:
                self._recent_request_addrs.pop(i)
                return

        # Check if the address has recently sent a request.
        for addr_ in self._recent_request_addrs:
            if addr_[0] == addr[0]:
                i = self._recent_request_addrs.index(addr_)
                # Update the time of the address.
                self._recent_request_addrs[i][1] = time.time()
                raise RecentRequestAddr

        # If the address has not been sent a request, add it to the list.
        self._recent_request_addrs.append([addr[0], time.time()])

    def _update_recent_request_addrs(self):
        '''
        Updates the list of recently received broadcast messages.
        '''
        for i, addr in enumerate(self._recent_request_addrs):
            if time.time() - addr[1] > self._recent_request_limit:
                self._recent_request_addrs.pop(i)


class RecentRequestAddr(Exception):
    '''
    Exception raised when a broadcast message is received from a recently received address.
    '''
    pass