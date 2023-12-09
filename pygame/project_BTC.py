import sys
import pygame
from math import floor
from pygame.locals import QUIT, Rect

pygame.init()
SURFACE = pygame.display.set_mode((800,800))
FPSCLOCK = pygame.time.Clock()

white = []
black = []
board = [[0]*10 for i in range(10)]
chess_click = False
dark_color = ((96,93,93))
bright_color = (140,140,140)

piece_font = pygame.font.SysFont(None, 100)


class Chess_piece:
    def __init__(self, x, y, piece, team):
        self.x = x
        self.y = y
        self.team = team
        self.piece = piece
        if self.team == 2:
            color = (0,0,0)
        else:
            color = (255,255,255)
        self.image = piece_font.render('{}'.format(self.piece), True, color)
    
    def move(self, mx, my):
        # 이동 시 다른 기물이 있는지 확인 후, 있으면 제거
        new_x, new_y = self.x + mx, self.y + my
        for piece in white + black:
            if piece.x == new_x and piece.y == new_y:
                piece.piece_remove()
                break

        self.x += mx
        self.y += my

    def piece_remove(self):
        if self in white:
            white.remove(self)
        elif self in black:
            black.remove(self)
        
    def draw(self):
        SURFACE.blit(self.image, (self.x*100+27, self.y*100+20))
        
    def is_check(self):
        # 해당 기물의 이동 가능한 위치를 모두 확인하여 상대 팀의 킹을 공격할 수 있는지 확인
        for i, j in movable(self):
            new_x, new_y = self.x + i, self.y + j
            for piece in white + black:
                if piece.piece == 'K' and piece.team != self.team:
                    if new_x == piece.x and new_y == piece.y:
                        return True
        return False

    def is_checkmate(self):
        # 해당 팀이 체크인 경우만 체크메이트 여부 확인
        if not self.is_check():
            return False

        # 해당 팀의 모든 기물에 대해 이동 가능한 위치를 확인하고, 이동해도 여전히 체크인 경우가 있는지 확인
        for piece in white + black:
            if piece.team == self.team:
                for i, j in movable(piece):
                    new_x, new_y = piece.x + i, piece.y + j
                    original_x, original_y = piece.x, piece.y

                    # 기물을 임시로 이동
                    piece.x, piece.y = new_x, new_y

                    # 체크 여부 확인
                    if not self.is_check():
                        # 체크가 되지 않는 경우, 기물을 원래 위치로 되돌리고 체크메이트가 아님
                        piece.x, piece.y = original_x, original_y
                        return False

                    # 체크가 되는 경우, 기물을 원래 위치로 되돌림
                    piece.x, piece.y = original_x, original_y

        # 모든 기물에 대해 이동해도 체크가 되는 경우, 체크메이트
        return True



class Pawn(Chess_piece):
    first = True
    def __init__(self, x, y, team):
        super().__init__(x,y, 'P', team)
        
class Rook(Chess_piece):
    def __init__(self, x, y, team):
        super().__init__(x,y, 'R', team)
        
class Knight(Chess_piece):
    def __init__(self, x, y, team):
        super().__init__(x,y, 'N', team)
        
class Bishop(Chess_piece):
    def __init__(self, x, y, team):
        super().__init__(x,y, 'B', team)
        
class Queen(Chess_piece):
    def __init__(self, x, y, team):
        super().__init__(x,y, 'Q', team)
        
class King(Chess_piece):
    def __init__(self, x, y, team):
        super().__init__(x,y, 'K', team)

def paint(chess_click, list, selected_piece):
    global dark_color
    global bright_color
    SURFACE.fill(dark_color)

    for x in range(8):
        for y in range(8):
            if x % 2 == 0 and y % 2 == 0:
                pygame.draw.rect(SURFACE, bright_color, Rect(x * 100, y * 100, 100, 100))
            elif x % 2 == 1 and y % 2 == 1:
                pygame.draw.rect(SURFACE, bright_color, Rect(x * 100, y * 100, 100, 100))

    if chess_click:
        chess_piece = list[1]
        chess_list = list[0]
        for i in chess_list:
            new_x, new_y = chess_piece.x + i[0], chess_piece.y + i[1]
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                pygame.draw.rect(SURFACE, (255, 255, 255), Rect(new_x * 100, new_y * 100, 100, 100), 5)

    for cp in white:
        cp.draw()

    for cp in black:
        cp.draw()

    if selected_piece and selected_piece.is_check():
        pygame.draw.rect(SURFACE, (255, 0, 0), Rect(selected_piece.x * 100, selected_piece.y * 100, 100, 100), 5)

    # 추가된 부분: 체크 시 빨간색 표시
    if selected_piece and selected_piece.is_check():
        pygame.draw.rect(SURFACE, (255, 0, 0), Rect(selected_piece.x * 100, selected_piece.y * 100, 100, 100), 5)

    # 추가된 부분: 체크메이트 시 승리 메시지
    if checkmate_winner:
        font = pygame.font.SysFont(None, 80)
        text = font.render(f"Player {checkmate_winner} Wins!", True, (255, 0, 0))
        SURFACE.blit(text, (200, 300))

    pygame.display.update()

    # 추가된 부분: 모든 위치에 대해 클릭 가능하도록 함
    if chess_click:
        for i in range(8):
            for j in range(8):
                pygame.draw.rect(SURFACE, (255, 255, 255), Rect(i * 100, j * 100, 100, 100), 1)


def game_init():
    global white
    global black

    for i in range(8):
        white.append(Pawn(i, 1, 1))
    for i in range(2):
        white.append(Rook(i*7, 0, 1))
        white.append(Knight(i*5+1, 0, 1))
        white.append(Bishop(i*3+2, 0, 1))
        
    white.append(Queen(3,0,1))
    white.append(King(4,0,1))
    
    for i in range(8):
        black.append(Pawn(i, 6, 2))
        
    for i in range(2):
        black.append(Rook(i*7, 7, 2))
        black.append(Knight(i*5+1, 7, 2))
        black.append(Bishop(i*3+2, 7, 2))
        
    black.append(Queen(3,7,2))
    black.append(King(4,7,2))
    
def make_board():
    global white
    global black
    global board
    
    board = [[0]*10 for i in range(10)]

    
    for i in white:
        board[i.y][i.x] = 1
        
    for i in black:
        board[i.y][i.x] = 2
                

    
def movable(chess):
    global white
    global board

    make_board()
    list = []
    check = True
    
    if chess.piece == 'P':
        if chess.team == 1:
            # 앞으로 이동
            if 0 <= chess.y + 1 < 8 and board[chess.y + 1][chess.x] == 0:
                list.append((0, 1))
                if chess.first and board[chess.y + 2][chess.x] == 0:
                    list.append((0, 2))

            # 대각선으로 공격
            if 0 <= chess.y + 1 < 8 and 0 <= chess.x + 1 < 8 and board[chess.y + 1][chess.x + 1] == 2:
                list.append((1, 1))

            if 0 <= chess.y + 1 < 8 and 0 <= chess.x - 1 < 8 and board[chess.y + 1][chess.x - 1] == 2:
                list.append((-1, 1))
        else:
            # 앞으로 이동
            if 0 <= chess.y - 1 < 8 and board[chess.y - 1][chess.x] == 0:
                list.append((0, -1))
                if chess.first and board[chess.y - 2][chess.x] == 0:
                    list.append((0, -2))

            # 대각선으로 공격
            if 0 <= chess.y - 1 < 8 and 0 <= chess.x + 1 < 8 and board[chess.y - 1][chess.x + 1] == 1:
                list.append((1, -1))

            if 0 <= chess.y - 1 < 8 and 0 <= chess.x - 1 < 8 and board[chess.y - 1][chess.x - 1] == 1:
                list.append((-1, -1))
                
    elif chess.piece == 'R':  # 룩
        for i in range(1, 8):
            if chess.y + i < 8:
                if board[chess.y + i][chess.x] == 0 and check:
                    list.append((0, i))
                elif board[chess.y + i][chess.x] != 0:
                    check = False
                    if board[chess.y + i][chess.x] != chess.team:
                        list.append((0, i))
                    break  # 첫 번째 발견된 이동 경로만 추가
                else:
                    break
        check = True

        for i in range(1, 8):
            if chess.y - i >= 0:
                if board[chess.y - i][chess.x] == 0 and check:
                    list.append((0, -i))
                elif board[chess.y - i][chess.x] != 0:
                    check = False
                    if board[chess.y - i][chess.x] != chess.team:
                        list.append((0, -i))
                    break  # 첫 번째 발견된 이동 경로만 추가
                else:
                    break

        check = True

        for i in range(1, 8):
            if chess.x + i < 8:
                if board[chess.y][chess.x + i] == 0 and check:
                    list.append((i, 0))
                elif board[chess.y][chess.x + i] != 0:
                    check = False
                    if board[chess.y][chess.x + i] != chess.team:
                        list.append((i, 0))
                    break  # 첫 번째 발견된 이동 경로만 추가
                else:
                    break

        check = True

        for i in range(1, 8):
            if chess.x - i >= 0:
                if board[chess.y][chess.x - i] == 0 and check:
                    list.append((-i, 0))
                elif board[chess.y][chess.x - i] != 0:
                    check = False
                    if board[chess.y][chess.x - i] != chess.team:
                        list.append((-i, 0))
                    break  # 첫 번째 발견된 이동 경로만 추가
                else:
                    break
             

    elif chess.piece == 'N':  # 나이트
        moves = [
            (1, 2), (-1, 2), (1, -2), (-1, -2),
            (2, 1), (-2, 1), (2, -1), (-2, -1)
        ]
        for move in moves:
            new_x, new_y = chess.x + move[0], chess.y + move[1]
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                if board[new_y][new_x] == 0 or board[new_y][new_x] != chess.team:
                    list.append(move)

    elif chess.piece == 'B':  # 비숍
        for i in range(1, 8):
            if chess.y + i < 8 and chess.x + i < 8:
                if board[chess.y + i][chess.x + i] == 0 and check:
                    list.append((i, i))
                elif board[chess.y + i][chess.x + i] != 0:
                    check = False
                    if board[chess.y + i][chess.x + i] != chess.team:
                        list.append((i, i))
                    break  # 첫 번째 발견된 이동 경로만 추가
                else:
                    break
        check = True

        for i in range(1, 8):
            if chess.y - i >= 0 and chess.x + i < 8:
                if board[chess.y - i][chess.x + i] == 0 and check:
                    list.append((i, -i))
                elif board[chess.y - i][chess.x + i] != 0:
                    check = False
                    if board[chess.y - i][chess.x + i] != chess.team:
                        list.append((i, -i))
                    break  # 첫 번째 발견된 이동 경로만 추가
                else:
                    break

        check = True

        for i in range(1, 8):
            if chess.y + i < 8 and chess.x - i >= 0:
                if board[chess.y + i][chess.x - i] == 0 and check:
                    list.append((-i, i))
                elif board[chess.y + i][chess.x - i] != 0:
                    check = False
                    if board[chess.y + i][chess.x - i] != chess.team:
                        list.append((-i, i))
                    break  # 첫 번째 발견된 이동 경로만 추가
                else:
                    break

        check = True

        for i in range(1, 8):
            if chess.y - i >= 0 and chess.x - i >= 0:
                if board[chess.y - i][chess.x - i] == 0 and check:
                    list.append((-i, -i))
                elif board[chess.y - i][chess.x - i] != 0:
                    check = False
                    if board[chess.y - i][chess.x - i] != chess.team:
                        list.append((-i, -i))
                    break  # 첫 번째 발견된 이동 경로만 추가
                else:
                    break
        check = True


    elif chess.piece == 'Q':
        for i in range(8):
            if i == 0:
                for k in range(chess.y + 1, 8):
                    if board[k][chess.x] == 0 and check:
                        list.append((0, k - chess.y))
                    elif board[k][chess.x] != 0:
                        check = False
                        if board[k][chess.x] != chess.team:
                            list.append((0, k - chess.y))
                        break  # 첫 번째 발견된 이동 경로만 추가
                    else:
                        break

            elif i == 1:
                for k in range(chess.y - 1, -1, -1):
                    if board[k][chess.x] == 0 and check:
                        list.append((0, k - chess.y))
                    elif board[k][chess.x] != 0:
                        check = False
                        if board[k][chess.x] != chess.team:
                            list.append((0, k - chess.y))
                        break  # 첫 번째 발견된 이동 경로만 추가
                    else:
                        break

            elif i == 2:
                for k in range(chess.x + 1, 8):
                    if board[chess.y][k] == 0 and check:
                        list.append((k - chess.x, 0))
                    elif board[chess.y][k] != 0:
                        check = False
                        if board[chess.y][k] != chess.team:
                            list.append((k - chess.x, 0))
                        break  # 첫 번째 발견된 이동 경로만 추가
                    else:
                        break

            elif i == 3:
                for k in range(chess.x - 1, -1, -1):
                    if board[chess.y][k] == 0 and check:
                        list.append((k - chess.x, 0))
                    elif board[chess.y][k] != 0:
                        check = False
                        if board[chess.y][k] != chess.team:
                            list.append((k - chess.x, 0))
                        break  # 첫 번째 발견된 이동 경로만 추가
                ####
            elif i == 4:
                for k in range(1, 8):
                    if chess.y + k < 9 and chess.x + k < 9:
                        if board[chess.y + k][chess.x + k] == 0 and check:
                            list.append((k, k))
                        elif board[chess.y + k][chess.x + k] != 0 and board[chess.y + k][chess.x + k] == chess.team:
                            break
                        else:
                            check = False
                            if board[chess.y + k][chess.x + k] != 0 and board[chess.y + k][chess.x + k] != chess.team:
                                list.append((k, k))
                                break  # 첫 번째 발견된 이동 경로만 추가

            elif i == 5:
                for k in range(1, 8):
                    if chess.x + k < 9 and chess.y - k >= 0:
                        if board[chess.y - k][chess.x + k] == 0 and check:
                            list.append((k, -k))
                        elif board[chess.y - k][chess.x + k] != 0 and board[chess.y - k][chess.x + k] == chess.team:
                            break
                        else:
                            check = False
                            if board[chess.y - k][chess.x + k] != 0 and board[chess.y - k][chess.x + k] != chess.team:
                                list.append((k, -k))
                                break  # 첫 번째 발견된 이동 경로만 추가

            elif i == 6:
                for k in range(1, 8):
                    if chess.y + k < 9 and chess.x - k >= 0:
                        if board[chess.y + k][chess.x - k] == 0 and check:
                            list.append((-k, k))
                        elif board[chess.y + k][chess.x - k] != 0 and board[chess.y + k][chess.x - k] == chess.team:
                            break
                        else:
                            check = False
                            if board[chess.y + k][chess.x - k] != 0 and board[chess.y + k][chess.x - k] != chess.team:
                                list.append((-k, k))
                                break  # 첫 번째 발견된 이동 경로만 추가

            elif i == 7:
                for k in range(1, 8):
                    if chess.y - k >= 0 and chess.x - k >= 0:
                        if board[chess.y - k][chess.x - k] == 0 and check:
                            list.append((-k, -k))
                        elif board[chess.y - k][chess.x - k] != 0 and board[chess.y - k][chess.x - k] == chess.team:
                            break
                        else:
                            check = False
                            if board[chess.y - k][chess.x - k] != 0 and board[chess.y - k][chess.x - k] != chess.team:
                                list.append((-k, -k))
                                break  # 첫 번째 발견된 이동 경로만 추가
            check = True
                    
            
                
    elif chess.piece == 'K':  # 킹
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if board[chess.y + i][chess.x + j] == 0 or board[chess.y + i][chess.x + j] != chess.team:
                    count += 1
                    list.append((j, i))
        
    return list
def piece_move(chess, list, x, y):
    global chess_click

    for i in list[0]:
        if x == chess.x + i[0] and y == chess.y + i[1]:
            # 목적지에 기물이 있는지 확인
            destination_piece = None
            for piece in white + black:
                if piece.x == x and piece.y == y:
                    destination_piece = piece
                    break

            # 목적지가 비어있으면 기물을 이동
            if destination_piece is None:
                chess.move(i[0], i[1])
            else:
                # 목적지의 기물을 제거하고 현재 기물을 이동
                destination_piece.piece_remove()
                chess.move(i[0], i[1])

            if chess.piece == 'P':
                chess.first = False

            chess_click = False
            break  # 첫 번째 성공적인 이동 이후에 루프 탈출
        # 추가된 부분: 상대 팀이 체크메이트인 경우 승리 메시지 출력
            checkmate_winner = 'white' if chess.team == 2 and chess.is_checkmate() else 'black' if chess.team == 1 and chess.is_checkmate() else None
            chess_click = False
            paint(chess_click, list, None, checkmate_winner)  # 추가된 부분: 체크메이트 여부를 paint 함수에 전달
            break  # 첫 번째 성공적인 이동 이후에 루프 탈출


def main():
    global white
    global black
    list = ()
    global chess_click
    selected_piece = None  # 선택된 기물을 저장할 변수

    game_init()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                xpos, ypos = floor(event.pos[0] / 100), floor(event.pos[1] / 100)

                # 이미 기물이 선택된 경우
                if chess_click and selected_piece:
                    piece_move(selected_piece, list, xpos, ypos)
                    selected_piece = None
                    chess_click = False
                else:
                    # 기물을 클릭한 경우 선택된 기물을 저장
                    for i in white + black:
                        if i.x == xpos and i.y == ypos and not chess_click:
                            selected_piece = i
                            list = (movable(i), i)
                            chess_click = True
                            break
                        elif i.x == xpos and i.y == ypos and chess_click:
                            selected_piece = i
                            list = (movable(i), i)
                            chess_click = True
                            break

        paint(chess_click, list, selected_piece)


if __name__ == "__main__":
    main()
