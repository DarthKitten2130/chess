import pygame as pg

pg.display.init()
w_size = ((pg.display.get_desktop_sizes()[0][0]) * 0.55, (pg.display.get_desktop_sizes()[0][1]) * 0.9)

class Tile(pg.sprite.Sprite):
    tilesize = w_size[1] // 8

    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.color = (255, 255, 255) if (x + y) % 2 == 0 else (51, 102, 0)
        self.rect = pg.Rect(x * self.tilesize, y * self.tilesize, self.tilesize, self.tilesize)
        self.image = pg.Surface((self.tilesize, self.tilesize))
        self.image.fill(self.color)


class Piece(pg.sprite.Sprite):
    def __init__(self, x, y, color, type):
        super().__init__()
        self.x = x
        self.y = y
        self.color = color
        self.image = pg.transform.scale_by(pg.image.load(f"images/{color}/{color}_{type}.png"),w_size[1] / 1440)
        self.rect = pg.Rect(x * Tile.tilesize, y * Tile.tilesize, Tile.tilesize, Tile.tilesize)
        self.movable_tiles = []
        self.moved = False


    def kill(self, live_pieces, dead_pieces):
        dead_pieces.add(self)
        live_pieces.remove(self)

    def outline(self, screen):
        pg.draw.rect(screen, (255, 0, 0), self.rect, 5)

    def check_moves(self, turn, chess_grid, live_pieces):
        mt = set()

        self.legal_move(chess_grid, live_pieces)
        original_x, original_y = self.x, self.y

        for coord in self.movable_tiles:
            simulated_grid = self.copy_chess_grid(chess_grid)
            simulated_grid[original_x][original_y] = None
            simulated_piece = simulated_grid[coord[0]][coord[1]] = self.__class__(coord[0], coord[1], self.color)
            simulated_piece.moved = self.moved

            simulated_pieces = []
            for i in range(8):
                for j in range(8):
                    if simulated_grid[i][j] is not None:
                        simulated_pieces.append(simulated_grid[i][j])
            simulated_king = next((p for p in simulated_pieces if isinstance(p, King) and p.color == turn), None)

            if not simulated_king.check(turn, simulated_pieces, simulated_grid):
                mt.add((coord[0], coord[1]))

        return mt

    @staticmethod
    def copy_chess_grid(chess_grid):
        new_grid = {i: {j: None for j in range(8)} for i in range(8)}
        for i in range(8):
            for j in range(8):
                if chess_grid[i][j] is not None:
                    piece = chess_grid[i][j]
                    new_grid[i][j] = piece.__class__(piece.x, piece.y, piece.color)
                    new_grid[i][j].movable_tiles = piece.movable_tiles.copy()
                    new_grid[i][j].moved = piece.moved
        return new_grid


class King(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color, "king")

    def kill(self, live_pieces, dead_pieces):
        raise AttributeError("Kings cannot be killed")

    def legal_move(self, chess_grid, live_pieces):
        lst = set()
        for i in range(self.x - 1, self.x + 2):
            for j in range(self.y - 1, self.y + 2):
                if 0 <= i <= 7 and 0 <= j <= 7 and (i, j) != (self.x, self.y):
                    if chess_grid[i][j] and chess_grid[i][j].color != self.color:
                        lst.add((i, j))
                    elif not chess_grid[i][j]:
                        lst.add((i, j))

        if not self.moved:
            try:
                l_rook = next((p for p in live_pieces if isinstance(p, Rook) and p.color == self.color and p.x == 0),
                              None)
                r_rook = next((p for p in live_pieces if isinstance(p, Rook) and p.color == self.color and p.x == 7),
                              None)
                if not chess_grid[1][self.y] and not chess_grid[2][self.y] and not chess_grid[3][
                    self.y] and not l_rook.moved:
                    lst.add((1, self.y))

                if not chess_grid[5][self.y] and not chess_grid[6][self.y] and not r_rook.moved:
                    lst.add((6, self.y))
            except AttributeError:
                pass
        self.movable_tiles = lst

    def castle(self, target, chess_grid):
        if self.moved or target.moved:
            return

        if self.color == "white":
            row = 7
        else:
            row = 0

        if target.x == 7:
            path = [5, 6]
            king_new_pos, rook_new_pos = (6, row), (5, row)
        elif target.x == 0:
            path = [1, 2, 3]
            king_new_pos, rook_new_pos = (2, row), (3, row)
        else:
            return

        for x in path:
            if chess_grid[x][row]:
                return

        chess_grid[self.x][self.y] = None
        chess_grid[target.x][target.y] = None
        self.x, self.y = king_new_pos
        target.x, target.y = rook_new_pos
        self.rect.topleft = (king_new_pos[0] * Tile.tilesize, king_new_pos[1] * Tile.tilesize)
        target.rect.topleft = (target.x * Tile.tilesize, target.y * Tile.tilesize)
        chess_grid[self.x][self.y] = self
        chess_grid[target.x][target.y] = target

    def check(self, turn, live_pieces, chess_grid):
        enemy_pieces = [piece for piece in live_pieces if piece.color != turn]

        king_pos = (self.x, self.y)

        for piece in enemy_pieces:
            piece.legal_move(chess_grid, live_pieces)

        for piece in enemy_pieces:
            if king_pos in piece.movable_tiles:
                return True

        return False


class Rook(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color, "rook")

    def legal_move(self, chess_grid, live_pieces):
        lst = set()
        for i in range(self.x + 1, 8):
            if chess_grid[i][self.y]:
                if chess_grid[i][self.y].color != self.color:
                    lst.add((i, self.y))
                break
            else:
                lst.add((i, self.y))

        for i in range(self.x - 1, -1, -1):
            if chess_grid[i][self.y]:
                if chess_grid[i][self.y].color != self.color:
                    lst.add((i, self.y))
                break
            else:
                lst.add((i, self.y))

        for j in range(self.y + 1, 8):
            if chess_grid[self.x][j]:
                if chess_grid[self.x][j].color != self.color:
                    lst.add((self.x, j))
                break
            else:
                lst.add((self.x, j))

        for j in range(self.y - 1, -1, -1):
            if chess_grid[self.x][j]:
                if chess_grid[self.x][j].color != self.color:
                    lst.add((self.x, j))
                break
            else:
                lst.add((self.x, j))

        self.movable_tiles = lst


class Bishop(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color, "bishop")

    def legal_move(self, chess_grid, live_pieces):
        lst = set()
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dx, dy in directions:
            i, j = self.x + dx, self.y + dy
            while 0 <= i <= 7 and 0 <= j <= 7:
                if chess_grid[i][j]:
                    if chess_grid[i][j].color != self.color:
                        lst.add((i, j))
                    break
                else:
                    lst.add((i, j))
                i += dx
                j += dy
        self.movable_tiles = lst


class Queen(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color, "queen")

    def legal_move(self, chess_grid, live_pieces):
        lst = set()
        b = Bishop(self.x, self.y, self.color)
        r = Rook(self.x, self.y, self.color)
        b.legal_move(chess_grid, live_pieces)
        r.legal_move(chess_grid, live_pieces)
        self.movable_tiles = b.movable_tiles | r.movable_tiles


class Knight(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color, "knight")

    def legal_move(self, chess_grid, live_pieces):
        lst = set()
        for i in range(-2, 3):
            for j in range(-2, 3):
                if abs(i) + abs(j) == 3:
                    if 0 <= self.x + i <= 7 and 0 <= self.y + j <= 7:
                        if chess_grid[self.x + i][self.y + j] and chess_grid[self.x + i][
                            self.y + j].color != self.color:
                            lst.add((self.x + i, self.y + j))

                        lst.add((self.x + i, self.y + j))
        self.movable_tiles = lst


class Pawn(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color, "pawn")
        self.en_passant = False

    def legal_move(self, chess_grid, live_pieces):
        lst = set()
        try:
            if not self.moved:
                if self.color == 'white':
                    if not chess_grid[self.x][self.y - 1]:
                        lst.add((self.x, self.y - 1))
                    if not chess_grid[self.x][self.y - 2]:
                        lst.add((self.x, self.y - 2))
                else:
                    if not chess_grid[self.x][self.y + 1]:
                        lst.add((self.x, self.y + 1))
                    if not chess_grid[self.x][self.y + 2]:
                        lst.add((self.x, self.y + 2))
            else:
                if self.color == 'white':
                    if not chess_grid[self.x][self.y - 1]:
                        lst.add((self.x, self.y - 1))
                else:
                    if not chess_grid[self.x][self.y + 1]:
                        lst.add((self.x, self.y + 1))

            if self.color == 'white':
                if self.x + 1 <= 7 and self.y - 1 >= 0 and chess_grid[self.x + 1][self.y - 1] and \
                        chess_grid[self.x + 1][self.y - 1].color != self.color:
                    lst.add((self.x + 1, self.y - 1))
                if self.x - 1 >= 0 and self.y - 1 >= 0 and chess_grid[self.x - 1][self.y - 1] and \
                        chess_grid[self.x - 1][self.y - 1].color != self.color:
                    lst.add((self.x - 1, self.y - 1))
            else:
                if self.x + 1 <= 7 and self.y + 1 <= 7 and chess_grid[self.x + 1][self.y + 1] and \
                        chess_grid[self.x + 1][self.y + 1].color != self.color:
                    lst.add((self.x + 1, self.y + 1))
                if self.x - 1 >= 0 and self.y + 1 <= 7 and chess_grid[self.x - 1][self.y + 1] and \
                        chess_grid[self.x - 1][self.y + 1].color != self.color:
                    lst.add((self.x - 1, self.y + 1))

            if self.x + 1 <= 7:
                right_piece = chess_grid[self.x + 1][self.y]
                if isinstance(right_piece, Pawn) and right_piece.color != self.color and right_piece.en_passant:
                    target_y = self.y - 1 if self.color == 'white' else self.y + 1
                    if 0 <= target_y <= 7:
                        lst.add((self.x + 1, target_y))

            if self.x - 1 >= 0:
                left_piece = chess_grid[self.x - 1][self.y]
                if isinstance(left_piece, Pawn) and left_piece.color != self.color and left_piece.en_passant:
                    target_y = self.y - 1 if self.color == 'white' else self.y + 1
                    if 0 <= target_y <= 7:
                        lst.add((self.x - 1, target_y))



        except (AttributeError, KeyError):
            pass
        self.movable_tiles = lst

    @staticmethod
    def promote(self, screen, live_pieces, dead_pieces, turn):
        popup = True
        selected = None

        pieces = []
        while popup:
            promos = pg.sprite.Group()
            promos.add(
                Queen(2, 3, turn),
                Bishop(3, 3, turn),
                Knight(4, 3, turn),
                Rook(5, 3, turn))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
                elif event.type == pg.MOUSEBUTTONUP:
                    mouse_pos = pg.mouse.get_pos()
                    for piece in promos:
                        if piece.rect.collidepoint(mouse_pos):
                            selected = type(piece).__name__
                            popup = False
                            promos.empty()
                            break
            pieces = {"Queen": Queen, "Bishop": Bishop, "Knight": Knight, "Rook": Rook}
            screen.fill((255, 87, 51))
            promos.draw(screen)
            pg.display.flip()

        self.kill(live_pieces, dead_pieces)
        self = pieces[selected](self.x, self.y, turn)
        live_pieces.add(self)
