from player import Player
import inputter

class Board:
    LOCAL = 0
    LAN = 1

    def __init__(self, mode=LOCAL) -> None:
        self.grid = [[' ' for _ in range(3)] for _ in range(3)]
        self.winner = None
        self.mode = mode

        self.player_x = Player()
        self.player_x.set_as_x()

        self.player_o = Player()
        self.player_o.set_as_o()

        self.turn = self.player_x


    def print(self) -> None:
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
        if self.turn.mode == Board.LOCAL:
            self._next_turn_local()
        elif self.turn.mode == Board.LAN:
            self._next_turn_lan()


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
        pass