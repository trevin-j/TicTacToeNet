# TicTacToeNet

# Overview

This piece of software is essentially a multiplayer tic-tac-toe game in the command line. It uses Python's socket module so that 2 instances of this software can communicate. My goal in writing this program was to learn about how networking works, and how Python can be used in networking.

Using the program is quite simple. It can be run by running the __main__.py script. To actually use this, though, you will need to run 2 instances of it. This could be 2 instances on the same computer, or on separate computers that are both on the same network. When you run 2 instances of the program, they *should* automatically find and connect to each other by the use of broadcast packets. If done on the same machine, this tends to work super well. However, occasionally there are issues that come up when using 2 separate computers. 

One issue causes the program to crash due to an IndexError, which I am in the process of finding and fixing. Another issue is being unable to find each other using broadcast packets. This second issue often is a result of a more restricted network, like appartment complex networks.

To do your turn, you enter the horizontal row, then the vertical column separated by a comma. They are 0 indexed, so a 0 indicates the first column or row.

[Software Demo Video](https://youtu.be/U9OyINk7BqM)

# Network Communication

The architecture used for this program is a peer-to-peer connection. The program uses both TCP and UDP for different reasons. UDP is used to send the broadcast packets, while TCP is used for the rest of the connection. 

The decision process behind TCP and UDP is that when sending broadcast packets, UDP doesn't require a connection, and can simply broadcast them for any devices listening to respond to. 

TCP is used during the rest of the program because with how this is structured, each packet **must** be received in full because it is a turn based game. Data is not constantly streaming back and forth, so if the packet doesn't make it to the destination, the game could have problems. And TCP needs a connection and also makes sure that the packet makes it to its destination.

The main port used is 12380. It is important to note, though, that when responding to a broadcast, the host responds on 12381 so that there are no conflicting messages.

The networking actually uses a little package that I am working on for easier networking. There are a lot of messy areas in the code, and it isn't documented super well, and there is a lot of room for improvement, but overall it does its job. This package has functions and classes that make networking just a little bit easier. This package is the lan directory in the project.

The MultiplayerGame class is a superclass that is designed to be implemented by the main game, in this case the Board class. It contains methods to set the game up for multiplayer (only turn-based multiplayer is really supported due to the lack of multithreading or asynchronous programming). This class interacts with broadcast_responder, client_handler, lan, and connection to connect clients, servers, and hosts.

The BroadcastResponder class is a subclass of Connection that uses UDP to respond to broadcasts and let them know a server or host exists.

The ClientHandler class is used by server/host to manage any connected clients. It is also a subclass of Connection.

The Connection class is less specific than the previous but represents a higher-level connection with methods that make networking easier.

One of the driving features of the Connection class is its ability to send dynamic length messages using headers. It sends a message of a specific length, which contains the length of the next message.

Lastly, the lan module contains a function which returns Connection objects representing hosts/servers on the local network.

# Development Environment

* Visual Studio Code
* Python 3.9
* Socket library

# Useful Websites

* [Official Python socket Docs](https://docs.python.org/3/library/socket.html)
* [GeeksforGeeks Python Socket Tutorial](https://www.geeksforgeeks.org/socket-programming-python/)

# Future Work

* Fix IndexError crash
* Support multithreading
* Add direct connect by ip, in case broadcast packet fails