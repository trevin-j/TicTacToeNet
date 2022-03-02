from game.board import Board
import debug.inputter as inputter

TEST_MODE = False
if TEST_MODE:
    inputter.set_test_file('test_input.txt')
    inputter.set_mode(inputter.TEST_MODE)



def main():
    board = Board(Board.LAN)

    while True:
        board.print()
        board.next_turn()
        if board.winner:
            break
        if board.cat:
            board.print()
            print('Cat\'s game!')
            break


if __name__ == '__main__':
    main()