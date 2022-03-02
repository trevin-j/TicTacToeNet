from game.player import Player
import debug.inputter as inputter
from lan.multiplayer_game import MultiplayerGame
from globals import MULTIPLAYER_PORT
import random
from cls import cls

class Board(MultiplayerGame):

    def __init__(self, mode=MultiplayerGame.LOCAL) -> None:
        self.grid = [[' ' for _ in range(3)] for _ in range(3)]
        self.winner = None
        self.mode = mode

        self.player_x = Player()
        self.player_x.set_as_x()

        self.player_o = Player()
        self.player_o.set_as_o()

        self.turn = self.player_x

        if mode == MultiplayerGame.LAN:
            self._port = MULTIPLAYER_PORT
            self._setup_lan()

    
    def _determine_player_roles(self):
        local_role = random.choice(('x', 'o'))
        if local_role == 'x':
            self.player_x.set_mode(MultiplayerGame.LOCAL)
            self.player_o.set_mode(MultiplayerGame.LAN)
        else:
            self.player_x.set_mode(MultiplayerGame.LAN)
            self.player_o.set_mode(MultiplayerGame.LOCAL)

        self.send_to_peer(local_role)
        

    def _retrieve_role(self) -> None:
        role = self.receive_from_peer()
        if role == 'x':
            self.player_x.set_mode(MultiplayerGame.LAN)
            self.player_o.set_mode(MultiplayerGame.LOCAL)
        else:
            self.player_x.set_mode(MultiplayerGame.LOCAL)
            self.player_o.set_mode(MultiplayerGame.LAN)



    def _setup_lan(self) -> None:
        print('Searching for existing games...')

        hosts = self.search_for_hosts()
        if len(hosts) > 0:
            print('Found game. Connecting...')
            self.connect_to_host(hosts[0])
            print('Connected. Determining roles...')
            self._retrieve_role()
            return
        
        print('No existing games found. Creating new game...')
        self.create_host()
    
        print('Waiting for client...')
        self.wait_and_connect_client()
        print('Connected. Determining roles...')
        self._determine_player_roles()


    def print(self) -> None:
        cls()
        for i in range(3):
            for k in range(3):
                print(' ' + self.grid[i][k], end=' ')
                if k < 2:
                    print('|', end='')
            if i < 2:
                print('\n---+---+---')
            else:
                print()


    def next_turn(self) -> None:
        if self.turn.mode == MultiplayerGame.LOCAL:
            self._next_turn_local()
        elif self.turn.mode == MultiplayerGame.LAN:
            self._next_turn_lan()

        self.cat = True
        for i in range(3):
            for k in range(3):
                if self.grid[i][k] == ' ':
                    self.cat = False


    def _switch_turn(self) -> None:
        if self.turn == self.player_x:
            self.turn = self.player_o
        else:
            self.turn = self.player_x


    def _next_turn_local(self) -> None:
        print(f'{self.turn.symbol}\'s turn')
        while True:
            try:
                row, col = inputter.get_input('row, col: ').split(',')
                row = int(row)
                col = int(col)
                if self.grid[row][col] != ' ':
                    print('Invalid move')
                    continue
                self.grid[row][col] = self.turn.symbol
                break
            except ValueError:
                print('Invalid input')
            except IndexError:
                print('Invalid move')

        if self.mode == MultiplayerGame.LAN:
            self.send_to_peer(f'{row},{col}')

        if self.check_winner():
            self.print_winner()

        self._switch_turn()


    def print_winner(self) -> None:
        self.print()
        print(f'{self.winner} wins!')


    def check_winner(self) -> bool:
        for i in range(3):
            if self.grid[i][0] != ' ' and self.grid[i][0] == self.grid[i][1] == self.grid[i][2]:
                self.winner = self.grid[i][0]
                return True
            if self.grid[0][i] != ' ' and self.grid[0][i] == self.grid[1][i] == self.grid[2][i]:
                self.winner = self.grid[0][i]
                return True
        if self.grid[0][0] != ' ' and self.grid[0][0] == self.grid[1][1] == self.grid[2][2]:
            self.winner = self.grid[0][0]
            return True
        if self.grid[0][2] != ' ' and self.grid[0][2] == self.grid[1][1] == self.grid[2][0]:
            self.winner = self.grid[0][2]
            return True
        return False

    def _next_turn_lan(self) -> None:
        print(f'{self.turn.symbol}\'s turn')
        print('Waiting on opponent...')

        opponent_turn = self.receive_from_peer()
        opponent_turn = opponent_turn.split(',')
        row = int(opponent_turn[0])
        col = int(opponent_turn[1])
        self.grid[row][col] = self.turn.symbol

        if self.check_winner():
            self.print_winner()

        self._switch_turn()