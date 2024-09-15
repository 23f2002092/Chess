from enum import IntEnum

class PieceType(IntEnum):
    NONE = 0
    PAWN = 1
    BISHOP = 2
    KNIGHT = 3
    ROOK = 4
    QUEEN = 5
    KING = 6
    WHITE = 8
    BLACK = 16

class Board:
    white_virgin = True
    black_virgin = True
    rook1 = True
    rook2 = True
    rook3 = True
    rook4 = True

    def __init__(self, game=None):
        if game is None:
            game = [[(PieceType.NONE, 0) for _ in range(8)] for _ in range(8)]
        self.game = game

    def reset(self):
        self.game = [[(PieceType.NONE, 0) for _ in range(8)] for _ in range(8)]

    def __str__(self):
        return str(self.game)

    def copy_board(self):
        return Board([row[:] for row in self.game])

    def path_is_clear(self, x1, y1, x2, y2):
        piece1, color1 = self.game[x1][y1]
        color2 = self.game[x2][y2][1]

        if color1 == color2:
            return False

        if piece1 == PieceType.PAWN:
            if y2 != y1 and self.game[x2][y2][0] == PieceType.NONE:
                return False
            if y2 == y1 and self.game[x2][y2][0] != PieceType.NONE:
                return False
            if abs(x2 - x1) == 2 and self.game[(x1 + x2) // 2][y1][0] != PieceType.NONE:
                return False

        x_diff = x2 - x1
        y_diff = y2 - y1

        if piece1 == PieceType.BISHOP or piece1 == PieceType.QUEEN:
            if abs(x_diff) == abs(y_diff):
                for i in range(1, abs(x_diff)):
                    if self.game[x1 + i * (x_diff // abs(x_diff))][y1 + i * (y_diff // abs(y_diff))][0] != PieceType.NONE:
                        return False

        if piece1 == PieceType.ROOK or piece1 == PieceType.QUEEN:
            if x_diff == 0 or y_diff == 0:
                for i in range(1, max(abs(x_diff), abs(y_diff))):
                    if self.game[x1 + i * (x_diff // abs(x_diff) if x_diff != 0 else 0)][y1 + i * (y_diff // abs(y_diff) if y_diff != 0 else 0)][0] != PieceType.NONE:
                        return False

        return True

    def valid_moves(self, x, y):
        piece, color = self.game[x][y]
        moves = []
        
        if piece == PieceType.PAWN:
            direction = -1 if color == PieceType.WHITE else 1
            start_row = 6 if color == PieceType.WHITE else 1
            if self.game[x + direction][y][0] == PieceType.NONE:
                moves.append((x + direction, y))
                if x == start_row and self.game[x + 2 * direction][y][0] == PieceType.NONE:
                    moves.append((x + 2 * direction, y))
            for dy in [-1, 1]:
                if 0 <= y + dy < 8 and self.game[x + direction][y + dy][1] == (PieceType.BLACK if color == PieceType.WHITE else PieceType.WHITE):
                    moves.append((x + direction, y + dy))

        elif piece == PieceType.BISHOP:
            for dx in [-1, 1]:
                for dy in [-1, 1]:
                    for i in range(1, 8):
                        nx, ny = x + dx * i, y + dy * i
                        if 0 <= nx < 8 and 0 <= ny < 8:
                            if self.game[nx][ny][0] == PieceType.NONE:
                                moves.append((nx, ny))
                            elif self.game[nx][ny][1] != color:
                                moves.append((nx, ny))
                                break
                            else:
                                break

        elif piece == PieceType.ROOK:
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                for i in range(1, 8):
                    nx, ny = x + dx * i, y + dy * i
                    if 0 <= nx < 8 and 0 <= ny < 8:
                        if self.game[nx][ny][0] == PieceType.NONE:
                            moves.append((nx, ny))
                        elif self.game[nx][ny][1] != color:
                            moves.append((nx, ny))
                            break
                        else:
                            break

        elif piece == PieceType.KNIGHT:
            for dx, dy in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8 and self.game[nx][ny][1] != color:
                    moves.append((nx, ny))

        elif piece == PieceType.QUEEN:
            moves += self.valid_moves(x, y, PieceType.ROOK)
            moves += self.valid_moves(x, y, PieceType.BISHOP)

        elif piece == PieceType.KING:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < 8 and 0 <= ny < 8 and self.game[nx][ny][1] != color:
                            moves.append((nx, ny))
            if color == PieceType.WHITE and self.white_virgin:
                if self.rook4 and all(self.game[7][y][0] == PieceType.NONE for y in [5, 6]):
                    moves.append((7, 6))
                if self.rook3 and all(self.game[7][y][0] == PieceType.NONE for y in [1, 2, 3]):
                    moves.append((7, 2))
            if color == PieceType.BLACK and self.black_virgin:
                if self.rook2 and all(self.game[0][y][0] == PieceType.NONE for y in [5, 6]):
                    moves.append((0, 6))
                if self.rook1 and all(self.game[0][y][0] == PieceType.NONE for y in [1, 2, 3]):
                    moves.append((0, 2))

        return moves

    def check_for_check(self, mouse):
        pieces = [(x, y) for x in range(8) for y in range(8) if self.game[x][y][0] != PieceType.NONE]
        black_king_pos = next(((x, y) for x, y in pieces if self.game[x][y] == (PieceType.KING, PieceType.BLACK)), None)
        white_king_pos = next(((x, y) for x, y in pieces if self.game[x][y] == (PieceType.KING, PieceType.WHITE)), None)

        if not white_king_pos:
            return [False]

        for x, y in pieces:
            if self.game[x][y][1] == PieceType.BLACK:
                if white_king_pos in self.valid_moves(x, y):
                    if self.path_is_clear(x, y, white_king_pos[0], white_king_pos[1]):
                        return [True, black_king_pos, white_king_pos]

        return [False]

    def move(self, x1, y1, x2, y2, check, original):
        if self.game[x1][y1] == (PieceType.NONE, 0):
            return 0

        if not (0 <= x1 < 8 and 0 <= y1 < 8 and 0 <= x2 < 8 and 0 <= y2 < 8):
            return 0

        if not self.path_is_clear(x1, y1, x2, y2):
            return 0

        temp_board = self.copy_board()
        temp_board.game[x2][y2], temp_board.game[x1][y1] = temp_board.game[x1][y1], (PieceType.NONE, 0)

        if self.check_for_check(-1)[0] and check != 8:
            return 0

        piece_type, piece_color = self.game[x1][y1]
        if piece_type == PieceType.KING:
            pieces_opponent = [
                (px, py) for px in range(8) for py in range(8)
                if self.game[px][py][1] != piece_color and self.game[px][py][1] != 0
            ]

            if piece_color == PieceType.WHITE:
                if (x2, y2) == (7, 6) and self.rook4 and all(self.game[7][y][0] == PieceType.NONE for y in [5, 6]) and not any((7, 5) in self.valid_moves(px, py) for px, py in pieces_opponent):
                    self.game[7][5], self.game[7][7] = self.game[7][7], (PieceType.NONE, 0)
                    if original:
                        self.white_virgin = False
                elif (x2, y2) == (7, 2) and self.rook3 and all(self.game[7][y][0] == PieceType.NONE for y in [1, 2, 3]) and not any((7, i) in self.valid_moves(px, py) for px, py in pieces_opponent for i in [1, 3]):
                    self.game[7][3], self.game[7][0] = self.game[7][0], (PieceType.NONE, 0)
                    if original:
                        self.white_virgin = False

            elif piece_color == PieceType.BLACK:
                if (x2, y2) == (0, 6) and self.rook2 and all(self.game[0][y][0] == PieceType.NONE for y in [5, 6]) and not any((0, 5) in self.valid_moves(px, py) for px, py in pieces_opponent):
                    self.game[0][5], self.game[0][7] = self.game[0][7], (PieceType.NONE, 0)
                    if original:
                        self.black_virgin = False
                elif (x2, y2) == (0, 2) and self.rook1 and all(self.game[0][y][0] == PieceType.NONE for y in [1, 2, 3]) and not any((0, i) in self.valid_moves(px, py) for px, py in pieces_opponent for i in [1, 3]):
                    self.game[0][3], self.game[0][0] = self.game[0][0], (PieceType.NONE, 0)
                    if original:
                        self.black_virgin = False

        if original:
            if (x1, y1) == (0, 0):
                self.rook1 = False
            elif (x1, y1) == (0, 7):
                self.rook2 = False
            elif (x1, y1) == (7, 0):
                self.rook3 = False
            elif (x1, y1) == (7, 7):
                self.rook4 = False

        self.game[x2][y2], self.game[x1][y1] = self.game[x1][y1], (PieceType.NONE, 0)

    def start(self):
        self.reset()
        self.game[0] = [(PieceType.ROOK, PieceType.BLACK), (PieceType.KNIGHT, PieceType.BLACK), (PieceType.BISHOP, PieceType.BLACK), (PieceType.QUEEN, PieceType.BLACK), (PieceType.KING, PieceType.BLACK), (PieceType.BISHOP, PieceType.BLACK), (PieceType.KNIGHT, PieceType.BLACK), (PieceType.ROOK, PieceType.BLACK)]
        self.game[1] = [(PieceType.PAWN, PieceType.BLACK) for _ in range(8)]
        self.game[6] = [(PieceType.PAWN, PieceType.WHITE) for _ in range(8)]
        self.game[7] = [(PieceType.ROOK, PieceType.WHITE), (PieceType.KNIGHT, PieceType.WHITE), (PieceType.BISHOP, PieceType.WHITE), (PieceType.QUEEN, PieceType.WHITE), (PieceType.KING, PieceType.WHITE), (PieceType.BISHOP, PieceType.WHITE), (PieceType.KNIGHT, PieceType.WHITE), (PieceType.ROOK, PieceType.WHITE)]
