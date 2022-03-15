import socket

from globals import dlogger

SPECIAL_CASE_MSGS = ['!CON!']

DYNAMIC_HEADER = '!DYNAMIC!(99999)'
DYNAMIC_HEADER_BYTES = len(DYNAMIC_HEADER)

'''
The connection class is used for communicating between players.
The main protocol for communications is TCP, however UDP is used to find LAN games.
'''

class Connection:

    def __init__(self, ip=None, port=None, socket=None):
        self._ip = ip
        self._port = port
        self._socket = socket
        self._msgs = []
        self._recvd_msgs = []

    def add_message(self, message):
        self._msgs.append(message)

    def tcp_connect(self):
        '''
        If a socket does not already exist for this connection and this connection was retrieved from a LAN server search, connect to the server.
        '''
        if self._socket is None:
            try:
                dlogger.log_info(f'Attempting to connect to {self._ip} at port {self._port}...')
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.connect((self._ip, self._port))
                dlogger.log_info(f'Connected to {self._ip} at port {self._port}.')
            except ConnectionRefusedError:
                dlogger.log_error(f'Connection refused from {self._ip} at port {self._port}. This is likely because the TCP port on the server is not open.')
                self._socket = None
        else:
            dlogger.log_warning('A socket already exists for this Connection object.')


    # Methods for receiving TCP messages

    def receive_tcp(self, bytes: int) -> bool:
        '''
        Receive bytes from the open tcp socket.
        Bytes are automatically converted into a string.
        String will be saved to end of self._recvd_msgs
        Args:
            bytes: the number of bytes to receive.
        Returns:
            True if the message was received, False if not.
        '''
        if self._socket is not None:
            try:
                dlogger.log_debug(f'Attempting to receive {bytes} bytes from TCP socket {self._ip} at port {self._port}...')
                self._recvd_msgs.append(self._socket.recv(bytes).decode('utf-8'))

                if len(self._recvd_msgs[-1]) == 0:
                    dlogger.log_debug('No TCP message received.')
                    self._recvd_msgs.pop()
                    return False

                dlogger.log_debug(f'Received {self._recvd_msgs[-1]} from TCP socket {self._ip} at port {self._port}.')
                return True

            except socket.timeout:
                dlogger.log_debug('No TCP message received.')
                return False

            except Exception as e:
                dlogger.log_error(f'Error receiving {bytes} bytes from TCP socket {self._ip} at port {self._port}.')
                dlogger.log_error(str(e))
                return False
        else:
            dlogger.log_error('No socket exists for this Connection object.')
            return False    
        

    def receive_tcp_all(self):
        '''
        Receive all msgs from a Connection and append them to self._recvd_msgs.
        Args:
            bytes: the number of bytes to receive.
        '''
        while self.dynamic_receive():
            pass


    def get_recvd_messages(self):
        return self._recvd_msgs

    def clear_recvd_messages(self):
        self._recvd_msgs = []

    # Methods for sending
    def send_tcp(self, message: str):
        '''
        Send a tcp message to the socket.
        Args:
            message: the message to send.
        Returns:
            True if the message was sent, False if not.
        '''
        if self._socket is not None:
            dlogger.log_info(f'Attempting to send {message} to TCP socket {self._ip} at port {self._port}...')
            self._socket.sendall(message.encode('utf-8'))
            return True
        else:
            dlogger.log_error('No socket exists for this Connection object.')
            return False

    def settimeout(self, timeout: int):
        '''
        Set the timeout for the socket.
        Args:
            timeout: the timeout in seconds.
        '''
        if self._socket is not None:
            self._socket.settimeout(timeout)
        else:
            dlogger.log_error('No socket exists for this Connection object.')

    
    # TCP Dynamic sending and receiving
    def dynamic_receive(self) -> bool:
        '''
        Receive a dynamic amount of bytes.
        This is done by having 2 msgs. One msg is the header and specifies the length of the next msg.
        '''
        is_special_case = True

        while is_special_case:
            dlogger.log_debug('Receiving dynamic message...')
            msg1_success = self.receive_tcp(DYNAMIC_HEADER_BYTES)

            if not msg1_success:
                return False
            
            msg1 = self._recvd_msgs[-1]

            if not DYNAMIC_HEADER[:9] in msg1:
                dlogger.log_warning(f'Dynamic receive was called, however {msg1} is not a dynamic message header.')
                self._recvd_msgs.pop()
                return False
            
            msg2_len = int(msg1[10:15])

            msg2_success = self.receive_tcp(msg2_len)

            if not msg2_success:
                dlogger.log_warning('2nd half of dynamic message failed to receive.')
                self._recvd_msgs.pop()
                self._recvd_msgs.pop()
                return False
            
            self._recvd_msgs.pop(-2)
            is_special_case = self._recvd_msgs[-1] in SPECIAL_CASE_MSGS
            if is_special_case:
                self._recvd_msgs.pop()

        return True
        
    def dynamic_send(self, msg):
        '''
        Sends a dynamic length msg.
        Returns True if sent, False otherwise.
        '''
        msg1 = f'!DYNAMIC!({len(msg):<5})'
        msg2 = msg

        if self.send_tcp(msg1):
            self.send_tcp(msg2)
            return True
        return False

    def close_socket(self):
        self._socket.close()
