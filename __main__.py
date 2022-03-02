from board import Board
import inputter

TEST_MODE = True
if TEST_MODE:
    inputter.set_test_file('test_input.txt')
    inputter.set_mode(inputter.TEST_MODE)



def main():
    board = Board(Board.LOCAL)

    while True:
        board.print()
        board.next_turn()
        if board.winner:
            break


if __name__ == '__main__':
    main()