import socket

from debug.dlogger import dLog
from globals import dlogger

from lan.connection import Connection

def check_lan_servers(port: int) -> tuple:
    '''
    Checks for LAN servers on the specified port.
    Any servers on LAN will respond with their IP address and any other data sent by the server will be returned as well.
    WARNING: Current implementation of this function WILL delay the program.
    Do NOT use in a part of the application where looping must be fast.
    It is solely intended to be used when in some sort of menu.
    A received message will come from port + 1 to reduce conjestion.
    Args:
        port: The port to check for servers.
    Returns:
        A touple of Connections, one for each server found.
    '''
    dlogger.log_warning('Function check_lan_servers does not run asnychronously and will take multiple seconds to return. Do not use where fast frame output is required.')

    dlogger.log_info('Sending broadcast packet on port ' + str(port))
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set the option to allow broadcast
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Bind to the port
    # sock.bind(('', port))

    # Create new socket for receiving message on port + 1
    sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_recv.bind(('', port + 1))

    # Broadcast UDP packets 3 times with a delay of 1 second between each
    for i in range(3):
        sock.sendto(b'PYMULT_BROADCAST', ('255.255.255.255', port))

    # Wait for 1 seconds for a response
    sock_recv.settimeout(1)
    connections = []
    try:
        # Continuously receive packets until timeout
        while True:
            msg1, addr1 = sock_recv.recvfrom(27)  # The first message contains exactly 27 bytes.
            dlogger.log_info('Received packet from ' + str(addr1))
            dlogger.log_info('Identifier: ' + str(msg1))

            # Make sure the message is valid
            if not(len(msg1) == 27 and 'PYMULT_SERVER_RESPONSE' in msg1.decode('utf-8')):
                dlogger.log_warning('Invalid message received. Ignoring.')
                continue

            # Determine the size of the next message.
            msg2_size = int(msg1.decode('utf-8')[23:26])
            dlogger.log_info('Message size: ' + str(msg2_size))

            # Receive the next message.
            msg2, addr2 = sock_recv.recvfrom(msg2_size)

            # If both messages came from different addresses, close socket and retry from the beginning.
            if addr1 != addr2:
                dlogger.log_warning('A message from one server was interrupted by another. Please retry checking LAN servers.')
                sock.close()
                sock_recv.close()
                connections.append(Connection.interrupted_server())
                break

            connections.append(Connection(ip=addr1[0], port=port))
            connections[-1].add_message(msg2.decode('utf-8'))
            dlogger.log_info('Message: ' + str(msg2))


    except socket.timeout:
        if len(connections) == 0:
            dlogger.log_info('No more servers found on port ' + str(port))

    # Close the socket
    sock.close()
    sock_recv.close()
    return connections