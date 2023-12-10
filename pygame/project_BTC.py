import sys
import pygame
from math import floor
from pygame.locals import QUIT, Rect, MOUSEBUTTONDOWN

pygame.init()
SURFACE = pygame.display.set_mode((1000,800))
FPSCLOCK = pygame.time.Clock()

white = []
black = []
board = [[0]*10 for i in range(10)]
chess_click = False
dark_color = ((96,93,93))
bright_color = (140,140,140)
turn = 1
piece_font = pygame.font.SysFont(None, 100)
# 버튼과 UI에 사용될 색상 및 폰트
button_color = (100, 100, 100)
ui_color = (150, 150, 150)
font = pygame.font.SysFont(None, 30)

# UI에 표시할 텍스트 및 버튼의 크기 및 위치 설정
text_buttons = [
    {"text": "Button 1", "rect": Rect(800, 50, 150, 50)},
    {"text": "Button 2", "rect": Rect(800, 700, 150, 50)},
]

ui_elements = [
    {"text": "UI Element 1", "rect": Rect(800, 350, 150, 50)},
    {"text": "UI Element 2", "rect": Rect(800, 450, 150, 50)},
]

def draw_button(text, rect):
    pygame.draw.rect(SURFACE, button_color, rect)
    button_text = font.render(text, True, (255, 255, 255))
    SURFACE.blit(button_text, (rect.x + 10, rect.y + 10))

def draw_ui_element(text, rect):
    pygame.draw.rect(SURFACE, ui_color, rect)
    ui_text = font.render(text, True, (0, 0, 0))
    SURFACE.blit(ui_text, (rect.x + 10, rect.y + 10))

# UI 및 버튼 그리기
def draw_ui():
    for element in ui_elements:
        draw_ui_element(element["text"], element["rect"])

    for button in text_buttons:
        draw_button(button["text"], button["rect"])

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
    
    def piece_remove(self):
        if self in white:
            white.remove(self)
        elif self in black:
            black.remove(self)
        
        # 삭제된 기물이 킹인지 확인하고 상대 팀의 승리 여부를 체크
        if self.piece == 'K':
            if self.team == 1:
                print("흰색 킹이 제거되었습니다. 상대 팀(검은색)의 승리입니다.")
            else:
                print("검은색 킹이 제거되었습니다. 상대 팀(흰색)의 승리입니다.")


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

def paint(chess_click, list, selected_piece, checkmate_winner=None):
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

    # 체크 상황에서 킹이 빨간색으로 표시
    for cp in white + black:
        if cp.is_check():
            pygame.draw.rect(SURFACE, (255, 0, 0), Rect(cp.x * 100, cp.y * 100, 100, 100), 5)

    pygame.display.update()

    # 모든 위치에 대해 클릭 가능하도록 함
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

def draw_start_screen():
    # 초기화면 그리기
    SURFACE.fill((0, 0, 0))  # 검은색 배경
    start_button_rect = Rect(400, 300, 200, 100)
    pygame.draw.rect(SURFACE, (100, 100, 100), start_button_rect)
    start_button_text = font.render("Game Start", True, (255, 255, 255))
    SURFACE.blit(start_button_text, (start_button_rect.x + 30, start_button_rect.y + 30))

    return start_button_rect

def start_screen():
    # 초기화면 처리
    start_button_rect = draw_start_screen()
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                if start_button_rect.collidepoint(event.pos):
                    return  # 게임 시작 버튼이 눌리면 함수 종료

        FPSCLOCK.tick(30)


def main():
    global white
    global black
    list = ()
    global chess_click
    selected_piece = None  # 선택된 기물을 저장할 변수
    start_screen() 
    game_init()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                xpos, ypos = floor(event.pos[0] / 100), floor(event.pos[1] / 100)

                # 버튼 클릭 확인
                for button in text_buttons:
                    if button["rect"].collidepoint(event.pos):
                        print(f"Button clicked: {button['text']}")

                # UI Element 클릭 확인
                for element in ui_elements:
                    if element["rect"].collidepoint(event.pos):
                        print(f"UI Element clicked: {element['text']}")

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
        draw_ui()  # UI 그리기
        pygame.display.update()
        FPSCLOCK.tick(30)

if __name__ == "__main__":
    main()


