import pygame as pg
import time
from classes import *


def main():
    pg.display.init()
    w_size = ((pg.display.get_desktop_sizes()[0][0]) * 0.55, (pg.display.get_desktop_sizes()[0][1]) * 0.9)
    screen = pg.display.set_mode(w_size)
    pg.display.set_caption('Chess')
    chess_grid = {i: {j: None for j in range(8)} for i in range(8)}
    board = pg.sprite.Group()
    live_pieces = pg.sprite.Group()
    dead_pieces = pg.sprite.Group()
    clicked_piece = None
    target = None
    turn = "white"
    moved = False
    checked = False

    pg.init()
    pg.font.init()
    t_size = int(64 * (w_size[1] / 1440))
    font = pg.font.SysFont('Arial', t_size)
    text = font.render("", True, (255, 255, 255))
    text_rect = text.get_rect(center = (w_size[0] // 2, w_size[1] // 2))
    for i in range(8):
        for j in range(8):
            board.add(Tile(i, j))

    live_pieces.add(
        Rook(7, 0, "black"),
        Rook(0, 0, "black"),
        Knight(6, 0, "black"),
        Knight(1, 0, "black"),
        Bishop(2, 0, "black"),
        Bishop(5, 0, "black"),
        Queen(3, 0, "black"),
        King(4, 0, "black"),
        Pawn(0, 1, "black"),
        Pawn(1, 1, "black"),
        Pawn(2, 1, "black"),
        Pawn(3, 1, "black"),
        Pawn(4, 1, "black"),
        Pawn(5, 1, "black"),
        Pawn(6, 1, "black"),
        Pawn(7, 1, "black"),
        Rook(0, 7, "white"),
        Rook(7, 7, "white"),
        Knight(1, 7, "white"),
        Knight(6, 7, "white"),
        Bishop(2, 7, "white"),
        Bishop(5, 7, "white"),
        Queen(3, 7, "white"),
        King(4, 7, "white"),
        Pawn(0, 6, "white"),
        Pawn(1, 6, "white"),
        Pawn(2, 6, "white"),
        Pawn(3, 6, "white"),
        Pawn(4, 6, "white"),
        Pawn(5, 6, "white"),
        Pawn(6, 6, "white"),
        Pawn(7, 6, "white")
    )

    def get_clicked_piece(live_pieces, mouse_pos):
        for piece in live_pieces:
            if piece.rect.collidepoint(mouse_pos):
                return piece
        return None

    def get_target(live_pieces, board, mouse_pos):
        for piece in live_pieces:
            if piece.rect.collidepoint(mouse_pos):
                return piece
        for tile in board:
            if tile.rect.collidepoint(mouse_pos):
                return tile
        return None

    def move(clicked_piece, target, turn, moved, chess_grid, screen, live_pieces, dead_pieces):
        chess_grid[clicked_piece.x][clicked_piece.y] = None
        clicked_piece.x, clicked_piece.y = target.x, target.y
        clicked_piece.rect.topleft = (target.x * Tile.tilesize, target.y * Tile.tilesize)
        chess_grid[target.x][target.y] = clicked_piece
        if isinstance(clicked_piece, Pawn) and clicked_piece.y in (0, 7):
            Pawn.promote(clicked_piece, screen, live_pieces, dead_pieces, turn)
        clicked_piece.movable_tiles.clear()
        if not clicked_piece.moved:
            clicked_piece.moved = True

        return True

    while True:
        t_king = next((p for p in live_pieces if isinstance(p, King) and p.color == turn), None)
        checked = t_king.check(turn, live_pieces, chess_grid)
        try:
            for pawn in [p for p in live_pieces if isinstance(p, Pawn) and p.color == turn]:
                if pawn.en_passant:
                    pawn.en_passant = False

        except AttributeError:
            pass

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.MOUSEBUTTONUP:
                mouse_pos = pg.mouse.get_pos()
                if not clicked_piece:
                    try:
                        clicked_piece = get_clicked_piece(live_pieces, mouse_pos)
                        mt = clicked_piece.check_moves(turn, chess_grid, live_pieces)
                        x = set()
                        for piece in (piece for piece in live_pieces if piece.color == turn):
                            a = piece.check_moves(turn, chess_grid, live_pieces)
                            x = x.union(a)

                        if not x and checked:
                            text = font.render("Checkmate! " + turn.capitalize() + " loses!", True, (255, 0, 0))
                            text_rect = text.get_rect(center=(w_size[0] // 2, w_size[1] // 2))

                            board.draw(screen)
                            live_pieces.draw(screen)
                            screen.blit(text, text_rect)
                            pg.display.flip()

                            wait_start = time.time()
                            while time.time() - wait_start < 5:
                                for event in pg.event.get():
                                    if event.type == pg.QUIT:
                                        pg.quit()
                                        quit()
                                pg.time.delay(100)

                            pg.quit()
                            quit()

                        elif not x and not checked:
                            text = font.render("Stalemate! No legal moves available!", True, (255, 0, 0))
                            text_rect = text.get_rect(center=(w_size[0] // 2, w_size[1] // 2))

                            board.draw(screen)
                            live_pieces.draw(screen)
                            screen.blit(text, text_rect)
                            pg.display.flip()

                            wait_start = time.time()
                            while time.time() - wait_start < 5:
                                for event in pg.event.get():
                                    if event.type == pg.QUIT:
                                        pg.quit()
                                        quit()
                                pg.time.delay(100)

                            pg.quit()
                            quit()


                    except AttributeError:
                        pass
                else:
                    if clicked_piece.color == turn:
                        target = get_target(live_pieces, board, mouse_pos)
                        if isinstance(target, Tile) and (target.x, target.y) and (target.x, target.y) != (
                                clicked_piece.x, clicked_piece.y) and (target.x, target.y) in mt:

                            if isinstance(clicked_piece, (King)) and clicked_piece.moved is False and (target.x,
                                                                                                       target.y) in [
                                (1, 0), (1, 7), (6, 0), (6, 7)] and (target.x, target.y) in mt:
                                if target.x == 1:
                                    rook = next((p for p in live_pieces if
                                                 isinstance(p, Rook) and p.x == 0 and p.color == turn), None)
                                    clicked_piece.castle(rook, chess_grid)
                                elif target.x == 6:
                                    rook = next((p for p in live_pieces if
                                                 isinstance(p, Rook) and p.x == 7 and p.color == turn), None)
                                    clicked_piece.castle(rook, chess_grid)

                                clicked_piece.movable_tiles.clear()
                                moved = True

                            else:
                                if (isinstance(clicked_piece, Pawn) and abs(clicked_piece.x - target.x) == 1 and
                                        abs(clicked_piece.y - target.y) == 1 and isinstance(target, Tile)):
                                        if turn == "white":
                                            if (isinstance(chess_grid[target.x][target.y + 1], Pawn) and
                                                    chess_grid[target.x][target.y + 1].color != turn):
                                                chess_grid[target.x][target.y + 1].kill(live_pieces, dead_pieces)
                                        elif turn == "black":
                                            if (isinstance(chess_grid[target.x][target.y - 1], Pawn) and
                                                    chess_grid[target.x][target.y - 1].color != turn):
                                                chess_grid[target.x][target.y - 1].kill(live_pieces, dead_pieces)

                                premove = clicked_piece.y
                                moved = move(clicked_piece, target, turn, moved, chess_grid, screen, live_pieces,
                                             dead_pieces)
                                postmove = clicked_piece.y
                                try:
                                    if (isinstance(clicked_piece,Pawn) and ((isinstance(chess_grid[clicked_piece.x+1][clicked_piece.y], Pawn) and
                                        chess_grid[clicked_piece.x+1][clicked_piece.y].color != turn)) and abs(premove-postmove) == 2 or
                                        ((isinstance(chess_grid[clicked_piece.x-1][clicked_piece.y], Pawn) and
                                         chess_grid[clicked_piece.x-1][clicked_piece.y].color != turn)) and abs(premove-postmove) == 2):
                                            clicked_piece.en_passant = True
                                except KeyError:
                                    pass

                        elif isinstance(target, Piece) and not isinstance(target,
                                                                          King) and target.color != clicked_piece.color and (
                                target.x, target.y) and (target.x, target.y) != (clicked_piece.x, clicked_piece.y) and (
                                target.x, target.y) in mt:
                            target.kill(live_pieces, dead_pieces)
                            moved = move(clicked_piece, target, turn, moved, chess_grid, screen, live_pieces,
                                         dead_pieces)

                        mt.clear()
                        clicked_piece = None
                        target = None
                        if moved:
                            if turn == "white":
                                turn = "black"
                            else:
                                turn = "white"
                            moved = False

                    else:
                        clicked_piece = None
                        target = None
                        continue

        for piece in live_pieces:
            chess_grid[piece.x][piece.y] = piece
        board.draw(screen)
        live_pieces.draw(screen)
        if clicked_piece:
            clicked_piece.outline(screen)
        screen.blit(text, text_rect)

        pg.display.flip()


if __name__ == '__main__':
    main()
