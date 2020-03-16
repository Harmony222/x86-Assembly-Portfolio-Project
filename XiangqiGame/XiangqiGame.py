# Author: Harmony Scarlet
# Date: 2/21/2020
# Description: Program to play the board game Xiangqi. Includes a XiangqiGame
#              class with methods get_game_state, is_in_check, and make_move.


class XiangqiGame:
    """
    Class that allows players to play the game Xiangqi. Includes get_game_state,
    is_in_check, and make_move methods.
    """
    def __init__(self):
        """ Initializes game data members. """
        self._game_state = "UNFINISHED"
        # build empty board, 10 rows with 9 columns each
        self._board = []
        for row in range(10):
            self._board.append([])
            for col in range(9):
                self._board[row].append("")

        self._red_pieces = []
        self._black_pieces = []
        # call set board method when game object is created
        self.set_board()
        # Keep track of player's General
        self._gen_red_loc = (0,4)
        self._gen_black_loc = (9,4)
        self._player_turn = 'red'

    def set_board(self):
        """
        Method used by the XiangqiGame class __init__ method to set up the board when a
        game instance is created. Creates all piece objects for each player and places them
        on the board.
        """
        players = ['red', 'black']
        # Set up and create pieces on rows 0(red) and 9(black)
        row = 0
        for player in players:
            self.set_piece(General, player, row, 4)
            self.set_piece(Advisor, player, row, 3)
            self.set_piece(Advisor, player, row, 5)
            self.set_piece(Elephant, player, row, 2)
            self.set_piece(Elephant, player, row, 6)
            self.set_piece(Horse, player, row, 1)
            self.set_piece(Horse, player, row, 7)
            self.set_piece(Chariot, player, row, 0)
            self.set_piece(Chariot, player, row, 8)
            row += 9
        # Set up and create pieces on rows 2(red) and 7(black)
        row = 2
        for player in players:
            self.set_piece(Cannon, player, row, 1)
            self.set_piece(Cannon, player, row, 7)
            row += 5
        # Set up and create pieces on rows 3(red) and 6(black)
        row = 3
        for player in players:
            for col in range(0,9,2):
                self.set_piece(Soldier, player, row, col)
            row += 3

    def set_piece(self, piece_class, player, row, col):
        """
        Used during board set-up to create piece objects and set them in place on the game
        board.
        """
        piece = piece_class(player, row, col)
        self.update_loc(piece, (row, col))
        # Add piece to list of red pieces or black pieces
        self._red_pieces.append(piece) if player == 'red' else self._black_pieces.append(piece)

    def update_loc(self, piece, loc):
        """ Update board location to hold piece. """
        self._board[loc[0]][loc[1]] = piece

    def get_game_state(self):
        """ Returns "UNFINISHED', 'RED_WON', or 'BLACK_WON' based on current game status."""
        return self._game_state

    def str_to_tuple(self, loc):
        """
        Converts square location from algebraic notation to integer tuple (row, column).
        Row range 0 to 9, column range 0 to 8.
        """
        row = int(loc[1:]) - 1
        # convert character to ASCII code and subtract 97 to correspond to 'a' = index of 0
        col = ord(loc[0]) - 97
        # return False if location out of board boundaries
        if not (0 <= row <= 9 and 0 <= col <= 8):
            return False
        return row, col

    def make_move(self, from_loc_alg, to_loc_alg):
        """
        Takes two parameters which are strings that represent the square moved from and
        the square moved to. Returns False if move is not legal, if square is not occupied
        by current player, or if game has been won.
        If valid move, returns True after move is made, captured piece removed, game
        status updated, and player turn is updated.
        """
        if self._game_state != "UNFINISHED":
            return False

        # Convert from algebraic notation to integer tuple (row, column)
        from_loc = self.str_to_tuple(from_loc_alg)
        to_loc = self.str_to_tuple(to_loc_alg)

        # return false if from_loc or to_loc is invalid
        if from_loc is False or to_loc is False:
            return False

        # return False if 'from' location empty
        if self._board[from_loc[0]][from_loc[1]] == "":
            return False
        # assign piece object at from_loc to 'piece' variable
        piece = self._board[from_loc[0]][from_loc[1]]

        # Return False if it is not the player's turn
        if piece.get_player() != self._player_turn:
            return False

        # set up opponent piece (if opponent piece exists)
        opponent_piece = None
        if self.is_occupied(to_loc):
            if self.occupied_by_opponent(piece, to_loc) is True:
                opponent_piece = self._board[to_loc[0]][to_loc[1]]
            # Return False if to_loc is occupied by current player
            else:
                return False

        # Get list of all valid moves for piece
        valid_moves = self.get_valid_moves(piece)

        # test to_loc to see if it puts current player in check
        if to_loc in valid_moves:
            test = self.test_move(piece, from_loc, to_loc, opponent_piece)
            if test is False:
                return False
            # if test_move is True, make move and capture opponent piece
            else:
                self.mov_piece(piece, from_loc, to_loc)
                # capture opponent piece if opponent piece exists
                if opponent_piece is not None:
                    self.capture_piece(opponent_piece)
        else:
            # return false if to_loc not in valid moves
            return False

        # Evaluate for checkmate and stalemate: check all opponent moves, if no move gets
        # opponent general out of check (checkmate) or if all opponent moves place their
        # player in check (stalemate), player wins
        if self._player_turn == "red":
            test = self.check_player_moves("black")
            if test is False:
                self._game_state = "RED_WON"

        if self._player_turn == "black":
            test = self.check_player_moves('red')
            if test is False:
                self._game_state = "BLACK_WON"

        # Change turns
        if self._player_turn == "red":
            self._player_turn = "black"
        else:
            self._player_turn = "red"
            self.print_board()

        # If all went smoothly with make-move, return True
        return True

    def is_in_check(self, player):
        """
        Takes as a parameter either 'red' or 'black' and returns True if that
        player is in check, otherwise returns False.
        """
        # Iterate through opponent player pieces and check their valid move locations,
        # if player's general's location is in one of their opponent's piece's valid
        # locations, the player is in check.
        if player == 'red':
            for piece in self._black_pieces:
                valid_moves = self.get_valid_moves(piece)
                if self._gen_red_loc in valid_moves:
                    return True
        if player == 'black':
            for piece in self._red_pieces:
                valid_moves = self.get_valid_moves(piece)
                if self._gen_black_loc in valid_moves:
                    return True
        # Check for flying general scenario. If generals are in the same column, check
        # the squares between them for a piece, if piece found, return False (not in check)
        if self._gen_red_loc[1] == self._gen_black_loc[1]:
            flying_general = True
            for row in range(self._gen_red_loc[0] + 1, self._gen_black_loc[0]):
                if self._board[row][self._gen_red_loc[1]] != "":
                    flying_general = False
            return flying_general
        # return False if player not in check
        return False

    def get_valid_moves(self, piece):
        """
        Gets potential move locations from the piece object and uses that information in
        combination with the current board state to return a set of valid moves for that
        pieces.
        """
        valid_moves = set()

        potential_moves = piece.get_movements(self._board)
        for move in potential_moves:
            if self.is_occupied(move) is False or self.occupied_by_opponent(piece, move) is True:
                valid_moves.add(move)

        return valid_moves

    def is_occupied(self, loc_tup):
        """ Returns True if location is occupied by any piece. """
        return self._board[loc_tup[0]][loc_tup[1]] != ""

    def occupied_by_opponent(self, piece, loc_tup):
        """ Returns True if location is occupied by opponent. """
        return self.is_occupied(loc_tup) \
               and self._board[loc_tup[0]][loc_tup[1]].get_player() != piece.get_player()

    def capture_piece(self, piece):
        """ Captures opponent piece. Updates piece loc to None and updates player piece list."""
        piece.set_loc((None, None))
        if piece.get_player() == "red":
            self._red_pieces.remove(piece)
        else:
            self._black_pieces.remove(piece)

    def check_player_moves(self, player):
        """
        Checks all player's current available moves, returns True if there is any
        valid move that does not place the player's general in check, otherwise
        returns False.
        """
        if player == "red":
            pieces_list = self._red_pieces
        else:
            pieces_list = self._black_pieces

        # Iterate through each piece in player piece list and test each piece's
        # available moves for validity
        for piece in pieces_list:
            from_loc = piece.get_loc()
            available_moves = self.get_valid_moves(piece)
            for move in available_moves:
                opp_piece = None
                # if occupied by opponent, assign opponent piece to piece located
                # at move location square
                if self.occupied_by_opponent(piece, move):
                    opp_piece = self._board[move[0]][move[1]]
                # run test move
                test = self.test_move(piece, from_loc, move, opp_piece)
                # return True once any valid move is found
                if test is True:
                    return True
        # return False if all available moves do not provide a valid move
        return False

    def test_move(self, piece, from_loc, to_loc, opponent_piece):
        """
        Used to test a move only, returns game to previous state before move.
        Makes a move and tests to see if that move places that player's general in
        check, then reverses the move.
        Returns False if test move places general in check, otherwise returns True.
        """
        # move piece from from_loc to to_loc
        self.mov_piece(piece, from_loc, to_loc)
        # capture opponent piece
        if opponent_piece is not None:
            self.capture_piece(opponent_piece)

        # test if player is in check after making move
        test = self.is_in_check(piece.get_player())

        # put player piece back
        self.mov_piece(piece, to_loc, from_loc)
        # put opponent piece back
        if opponent_piece is not None:
            self.update_loc(opponent_piece, to_loc)
            opponent_piece.set_loc(to_loc)
            if opponent_piece.get_player() == "red":
                self._red_pieces.append(opponent_piece)
            else:
                self._black_pieces.append(opponent_piece)

        # if making the move placed the current player in check (in-check test is True),
        # it is not a valid move and function returns False
        if test is True:
            return False
        else:
            return True

    def mov_piece(self, piece, from_loc, to_loc):
        """
        Moves piece from from_loc to to_loc: updates piece object location, updates
        board to_loc square to hold piece, empties from_loc square, if piece is a
        General, updates game general location.
        """
        # set piece's location
        piece.set_loc(to_loc)

        # update board, add piece to to_loc
        self.update_loc(piece, to_loc)
        # remove piece from previous location
        self.update_loc("", from_loc)

        # update general tracking
        if piece.get_id() == "Ge":
            if piece.get_player() == "red":
                self._gen_red_loc = to_loc
            if piece.get_player() == "black":
                self._gen_black_loc = to_loc

    def print_board(self):
        """ Prints the board at the current state. """
        columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
        print("      ", end="")
        for char in columns:
            print("   " + char + "   ", end="")
        print()
        print("      ", end="")
        for i in range(9):
            print("   " + str(i) + "   ", end="")
        print()

        for j in range(9, -1, -1):
            print(str(j) + "(" + str(j+1) + ")", end=" ")
            if j < 9:
                print(" ", end="")
            row = self._board[j]
            for i in range(9):
                if row[i] != "":
                    print("[", row[i], "]", end="")
                else:
                    print("[     ]", end="")
            print()

        print(self.get_game_state())


class Piece:
    """
    Parent class for Xiangqi pieces. Sets up basic data members and basic methods.
    """
    def __init__(self, player, row, col):
        """ Initialize piece data members. """
        self._player = player
        self._row = row
        self._col = col
        self._id = None

        # set of all possible tuples for board
        self._boundaries = {(row,col) for row in range(0,10) for col in range(0,9)}

    def __repr__(self):
        """ Display object player + id when printing piece objects. """
        if self._player == 'red':
            return 'r' + self._id
        else:
            return 'b' + self._id

    def get_id(self):
        """ Return piece id. """
        return self._id

    def get_loc(self):
        """ Return piece location as a tuple. """
        return self._row, self._col

    def set_loc(self, loc):
        """ Set piece location. """
        self._row = loc[0]
        self._col = loc[1]

    def get_player(self):
        """ Get piece's player. """
        return self._player

    def get_movements(self):
        """ Get piece movements. """
        pass

    def in_bounds(self, loc):
        """
        Return True if location is in game board boundaries, otherwise returns
        False.
        """
        return 0 <= loc[0] <= 9 and 0 <= loc[1] <= 8

    def get_adjacent(self):
        """ Returns set of board locations adjacent to piece. """
        adjacent = set()
        idx_adjacent = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for idx in idx_adjacent:
            adjacent.add((self._row + idx[0], self._col + idx[1]))

        return {move for move in adjacent if self.in_bounds(move) is True}

    def get_diagonals(self):
        """ Returns set of board locations diagonal to piece. """
        diagonals = set()
        idx_diagonals = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for idx in idx_diagonals:
            diagonals.add((self._row + idx[0], self._col + idx[1]))

        return {move for move in diagonals if self.in_bounds(move) is True}


class General(Piece):
    """ Represents a General piece, inherits from Piece class. """
    def __init__(self, player, row, col):
        """ Initializes data members. """
        super().__init__(player, row, col)
        self._id = 'Ge'
        # General's boundaries are within the palace on each side
        if player == 'red':
            self._boundaries = {(row,col) for row in range(0,3) for col in range(3,6)}
        if player == 'black':
            self._boundaries = {(row,col) for row in range(7,10) for col in range(3,6)}

    def get_movements(self, board):
        """
        Returns a set of potential moves based on allowed general moves (1 square
        orthogonally) and general boundaries (in palace).
        """
        return self.get_adjacent() & self._boundaries


class Advisor(Piece):
    """ Represents an Advisor piece, inherits from Piece class. """
    def __init__(self, player, row, col):
        """ Initializes data members. """
        super().__init__(player, row, col)
        self._id = 'Ad'
        # Advisor's boundaries are in palace, restricted to diagonals and center
        if player == 'red':
            self._boundaries = {(0,3), (0,5), (1,4), (2,3), (2,5)}
        if player == 'black':
            self._boundaries = {(7,3), (7,5), (8,4), (9,3), (9,5)}

    def get_movements(self, board):
        """
        Returns a set of potential moves based on allowed Advisor move (1 square
        diagonal) and Advisor boundaries (in palace).
        """
        return self.get_diagonals() & self._boundaries


class Elephant(Piece):
    """ Represents an Elephant piece, inherits from Piece class. """
    def __init__(self, player, row, col):
        """ Initializes data members. """
        super().__init__(player, row, col)
        self._id = 'El'
        # Elephant boundaries are the 7 squares it can legally move to
        if player == 'red':
            self._boundaries = {(0,2), (0,6), (2,0), (2,4), (2,8), (4,2), (4,6)}
        if player == 'black':
            self._boundaries = {(5,2), (5,6), (7,0), (7,4), (7,8), (9,2), (9,6)}

    def get_movements(self, board):
        """ Returns a set of potential moves for elephant. """
        # get 1st diagonal away from elephant, if square is occupied, elephant cannot move
        # in that direction
        diagonals1 = {loc for loc in self.get_diagonals() if board[loc[0]][loc[1]] == ""}

        # get positions 1 diagonal away from the 1st diagonal
        diagonals2 = set()
        idx_diagonals = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for loc in diagonals1:
            for idx in idx_diagonals:
                diagonals2.add((loc[0] + idx[0], loc[1] + idx[1]))

        # Create set of locations based on elephant moving 2 points diagonally
        movements = set()
        idx_movements = [(2, 2), (2, -2), (-2, 2), (-2, -2)]
        for idx in idx_movements:
            movements.add((self._row + idx[0], self._col + idx[1]))

        # Return intersection of diagonals, movements, and boundaries
        return diagonals2 & movements & self._boundaries


class Horse(Piece):
    """ Represents a Horse piece, inherits from Piece class."""
    def __init__(self, player, row, col):
        """ Initializes data members. """
        super().__init__(player, row, col)
        self._id = 'Ho'

    def get_movements(self, board):
        """ Returns a set of potential moves for horse. """
        # get 1st adjacent squares from Horse, if place is occupied, Horse cannot move in that
        # direction
        adjacent = {loc for loc in self.get_adjacent() if board[loc[0]][loc[1]] == ""}

        # Get positions 1 diagonal from the adjacent position.
        diagonal_from_adjacent = set()
        idx_diagonals = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for loc in adjacent:
            for idx in idx_diagonals:
                diagonal_from_adjacent.add((loc[0] + idx[0], loc[1] + idx[1]))

        # Create set of locations based on allowed horse movements
        movements = set()
        idx_horse = [(-1, -2), (-1, 2), (1, -2), (1, 2), (-2, -1), (-2, 1), (2, -1), (2, 1)]
        for idx in idx_horse:
            movements.add((self._row + idx[0], self._col + idx[1]))

        # Return intersection of diagonal_from_adjacent, movements, and boundaries
        return diagonal_from_adjacent & movements & self._boundaries


class Chariot(Piece):
    """ Represents a Chariot Piece, inherits from Piece class. """
    def __init__(self, player, row, col):
        """ Initializes data members. """
        super().__init__(player, row, col)
        self._id = 'Ch'

    def get_movements(self, board):
        """ Return a set of valid movements for Chariot. """
        valid_moves = set()
        idx = [-1, 1]
        # Starting adjacent to player in each direction, check if each square is empty,
        # if empty, add loc to valid moves, add to valid moves if occupied by opponent.
        # Once any occupied square is found, stop searching in that direction.
        for i in idx:
            square_row = self._row + i
            square_col = self._col
            while 0 <= square_row <= 9:
                if board[square_row][square_col] == "":
                    valid_moves.add((square_row, square_col))
                    square_row += i
                else:

                    if board[square_row][square_col].get_player() != self._player:
                        valid_moves.add((square_row, square_col))
                    break

        for i in idx:
            square_row = self._row
            square_col = self._col + i
            while 0 <= square_col <= 8:
                if board[square_row][square_col] == "":
                    valid_moves.add((square_row, square_col))
                    square_col += i
                else:
                    if board[square_row][square_col].get_player() != self._player:
                        valid_moves.add((square_row, square_col))
                    break

        return valid_moves


class Cannon(Piece):
    """ Represents a Cannon Piece, inherits from Piece class. """
    def __init__(self, player, row, col):
        """ Initializes data members. """
        super().__init__(player, row, col)
        self._id = 'Ca'

    def get_movements(self, board):
        """ Return a set of valid movements for Cannon piece. Starting adjacent to player
        in each direction, check if each square is empty, if empty, add loc to valid moves.
        If square is occupied, start checking on other side of occupied square, if an
        opponent square is found, that square is a valid move, all other squares after
        an occupied square are not valid moves."""

        valid_moves = set()
        idx = [-1, 1]
        # Column stays the same, check up and down
        for i in idx:
            square_row = self._row + i
            square_col = self._col
            # starting adjacent to player in the same column, if loc empty, add to valid moves
            while 0 <= square_row <= 9:
                if board[square_row][square_col] == "":
                    valid_moves.add((square_row, square_col))
                    square_row += i
                else:
                    # if loc occupied, skip over and keep checking until end of column
                    square_row += i
                    while 0 <= square_row <= 9:
                        # if empty, it is not a valid move (piece already jumped 1 piece)
                        if board[square_row][square_col] == "":
                            square_row += i
                        else:
                            # valid move if a square is occupied by opponent
                            if board[square_row][square_col].get_player() != self._player:
                                valid_moves.add((square_row, square_col))
                            break
                    break
        # row stays the same, check left and right
        for i in idx:
            square_row = self._row
            square_col = self._col + i
            # starting adjacent to player in the same row, if loc empty, add to valid moves
            while 0 <= square_col <= 8:
                if board[square_row][square_col] == "":
                    valid_moves.add((square_row, square_col))
                    square_col += i
                else:
                    # if loc occupied, skip over and keep checking until end of row
                    square_col += i
                    while 0 <= square_col <= 8:
                        # if empty, it is not a valid move (piece already jumped 1 piece)
                        if board[square_row][square_col] == "":
                            square_col += i
                        else:
                            # valid move if a square is occupied by opponent
                            if board[square_row][square_col].get_player() != self._player:
                                valid_moves.add((square_row, square_col))
                            break
                    break

        return valid_moves

class Soldier(Piece):
    """ Represents a Soldier Piece, inherits from Piece class. """
    def __init__(self, player, row, col):
        """ Initializes data members. """
        super().__init__(player, row, col)
        self._id = "So"

    def get_movements(self, board):
        """
        Creates a set of potential movements based on allowed moves (forward 1 square
        until they cross the river, then forward 1 square or orthogonal 1 square.
        Returns a set of potential movements based on movement set and board boundaries.
        """
        movements = set()
        if self._player == 'red':
            if self._row >= 5:
                movements = {
                    (self._row, self._col - 1),             # left
                    (self._row, self._col + 1),             # right
                    (self._row + 1, self._col)              # up
                }
            else:
                movements = {(self._row + 1, self._col)}    # up

        if self._player == 'black':
            if self._row <= 4:
                movements = {
                    (self._row, self._col - 1),             # left
                    (self._row, self._col + 1),             # right
                    (self._row - 1, self._col)              # down
                }
            else:
                movements = {(self._row - 1, self._col)}    # down

        return movements & self._boundaries


def main():
    game1 = XiangqiGame()
    game1.print_board()

    print(game1.make_move('b3', 'e3'))
    print(game1.make_move('h8', 'e8'))

    print(game1.make_move('h3', 'h6'))
    print(game1.make_move('b8', 'b4'))

    print(game1.make_move('e3', 'e7'))
    print('black is in check', game1.is_in_check('black'))
    print(game1.make_move('e8', 'e4'))

    print(game1.make_move('h6', 'e6'))
    print('black is in check', game1.is_in_check('black'))
    print(game1.get_game_state())

if __name__ == '__main__':
    main()