from game.board import Board

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