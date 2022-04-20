import numpy as np
import copy
import pygame
import sys

from patchwork_background import *
from tiles_data import tiles_list


pygame.init()
#pygame.mixer.init()
#pygame.mixer.music.load("tl.mp3") 
#pygame.mixer.music.play(-1)

BLACK_THEME = [(225, 0, 0), (0, 0, 225), (0, 225, 0), (0, 225, 0), (225, 225, 225), (0,255,255), (0, 0, 0), (100, 100, 100), (150, 28, 200), (1, 202, 225)]
WHITE_THEME = [(128, 0, 128), (128, 0, 0), (128, 0, 128),(25, 25, 112),(188, 143, 143),(61, 37, 2),(248, 248, 255),(176, 196, 222),(30, 144, 255),(199, 21, 133)]
#YELLOW_THEME = [(60 179 113), (128, 0, 0), (60 179 113), (123, 104, 23), (160, 82, 45), (61, 37, 2), (255, 215, 0), (210, 105, 30), (30,144,255), (199, 21, 133)]
YELLOW_THEME = [(102,0,0), (128, 128, 0), (102,0,0),(0, 128, 0),(160, 82, 45),(61, 37, 2),(255,215,0),(210,105,30),(148, 0, 211),(222, 0, 0)]
RED_THEME = [(255, 140, 0),(128, 0, 128),(255, 140, 0),(65, 105, 225),(28,0,0),(225,225,225),(178, 34, 34),(10, 0, 0),(0, 128, 0),(25, 25, 112)]
GREEN_THEME = [(242, 183, 94),(220, 20, 60),(242, 183, 94),(242, 155, 174),(85, 107, 47),(51,23,0),(166, 242, 141),(1, 92, 48),(138, 43, 226),(240, 230, 140)]

t_ind = 0
THEMES = [BLACK_THEME, WHITE_THEME, YELLOW_THEME, RED_THEME, GREEN_THEME]
SETTED_TILE_COLOR, BUTTON_COLOR, SP_TILE_COLOR, FREE_TILE_COLOR, NORM_COLOR, TEXT_COLOR, SCREEN_COLOR, TIMELINE_COLOR, FIRST_PLAYER_COLOR, SECOND_PLAYER_COLOR = THEMES[t_ind]
#[(0, 250, 154),(225, 0, 0)]
#SETTED_TILE_COLOR = (232, 187, 121)
#BUTTON_COLOR = (220, 20, 60)
#SP_TILE_COLOR = (232, 187, 121)
#FREE_TILE_COLOR = (255, 182, 193)
#NORM_COLOR = (85, 107, 47)
#TEXT_COLOR = (51,23,0)
#SCREEN_COLOR = (166, 242, 141)
#TIMELINE_COLOR = (1, 92, 48)
#FIRST_PLAYER_COLOR = (138, 43, 226)
#SECOND_PLAYER_COLOR = (240, 230, 140)

size = (1100, 510)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("mega_game")
GAME_FONT = pygame.font.Font('your_font.ttf', 24)

num_cells_timeline= 54 
button_income_coords = [4,10,16,24,31,38,44,51] 
special_tiles_coords = [20,28,35,48,52]

widht = height = 40
margin = 5
field_1 = QuiltBoard(np.zeros((9, 9), dtype=bool))
field_2 = QuiltBoard(np.zeros((9, 9), dtype=bool))
running = True
ind = -1
common_tiles = [Tile(2,0,1,[[True,True]])]
tile = common_tiles[-1]


def text_objects(text, font):
    textSurface = font.render(text, True, TEXT_COLOR)
    # Create the text rect.
    textRect = textSurface.get_rect()
    # Return a tuple consisting of the surface and the rect.
    return textSurface, textRect

def draw_game_tip():
    keystate = pygame.key.get_pressed()
    if keystate[pygame.K_h]:
        tip_image = pygame.image.load("rules.png")
        tip_sf = pygame.Surface(size)
        tip_sf.fill((0,0,0))
        textSurf, TextRect = text_objects('правила', GAME_FONT)
        tip_sf.blit(textSurf, TextRect)
        screen.blit(tip_sf, (0,0))
        screen.blit(tip_image, (0,0))
        

def draw_timeline(special_tile_coords, button_income_coords,
                  first_player, second_player):
    keystate = pygame.key.get_pressed()
    if keystate[pygame.K_t]:
        timeline_screen = pygame.Surface(size)
        timeline_screen.fill(SCREEN_COLOR)
        square = pygame.Surface((40,40))
        square.fill(NORM_COLOR)
        x = 5
        y = 5
        for i in range(54):  #54
            square.fill(TIMELINE_COLOR)
            if i in special_tile_coords:  #  определяем функциональный тип клетки
                square.fill(SP_TILE_COLOR)
            if i in button_income_coords:
                square.fill(BUTTON_COLOR)
            if i == first_player:
                square.fill(FIRST_PLAYER_COLOR)
            if i == second_player:
                square.fill(SECOND_PLAYER_COLOR)

            square_num = i % 22  #  тип по позиции на таймлайне
            timeline_screen.blit(square, (x, y))
            if square_num  < 9:
                x += 45
            elif square_num in {9, 10, 20, 21}:
                y += 45
            elif square_num < 20:
                x -= 45
        screen.blit(timeline_screen, (0,0))

def action_A(player_1, player_2, timeline):
    moving_player = timeline.current_player
    time_move = abs(player_1.time_coords - player_2.time_coords) +1
    moving_player.num_buttons += time_move
    timeline.move(time_move)
    timeline.buttons_income(time_move)
    timeline.special_tiles(time_move)
    


def count_scores(player):
    total_score = 0
    total_score += player.num_buttons
    if player.is_bonus:
        total_score += 7
    total_score -= 2*player.players_field.empty_cells_left()
    return total_score


is_bonus = False
for t in tiles_list:
    if len(t) !=4:
        print(len(t))
        raise ValueError('Tile must contain only base configuration, price, income and time in this order.')
    conf = t[0]
    price = t[1]
    income = t[2]
    time = t[3]
    new_tile = Tile(price,income,time,conf)
    common_tiles.append(new_tile)
# start_board = empty_field = np.zeros((FIELD_HEIGHT, FIELD_WIDTH), dtype=bool)
q_board_1 = QuiltBoard(np.zeros((FIELD_HEIGHT, FIELD_WIDTH), dtype=bool))
q_board_2 = QuiltBoard(np.zeros((FIELD_HEIGHT, FIELD_WIDTH), dtype=bool))
player_1 = Player(q_board_1, 'Игрок 1')
player_2 = Player(q_board_2, 'Игрок 2')
timeline = TimeLine(num_cells_timeline, button_income_coords, special_tiles_coords, player_1, player_2)

while running:
    screen.fill(SCREEN_COLOR)
    textSurf, TextRect = text_objects(f"Текущий игрок: {timeline.current_player.name}, количество пуговиц: {timeline.current_player.num_buttons}, количество кусков кожи: {timeline.current_player.num_special_tiles}", GAME_FONT)
    screen.blit(textSurf, (100,420))
    textSurf2, TextRec2 = text_objects(f"Зажмите h чтобы увидеть подсказки", GAME_FONT)
    screen.blit(textSurf2, (300,460))
    textSurf3, TextRect3 = text_objects(f'Цена: {tile.price}', GAME_FONT)
    textSurf4, TextRect4 = text_objects(f'Доход: {tile.income}', GAME_FONT)
    textSurf5, TextRect5 = text_objects(f'Время:{tile.time}', GAME_FONT)
    screen.blit(textSurf3, (920,150))
    screen.blit(textSurf4, (920,200))
    screen.blit(textSurf5, (920,250))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit(0)

        elif event.type == pygame.KEYDOWN:                
            if event.key == pygame.K_q:
                cur_tiles = common_tiles[:3]
                ind+=1
                if ind > len(cur_tiles) - 1:
                    ind = 0

                tile=cur_tiles[ind]

            elif event.key == pygame.K_a:
                action_A(player_1, player_2, timeline)
                timeline.whose_turn()  #передача хода

            elif event.key == pygame.K_r:
                tile.choose_next_configuration()

            elif event.key == pygame.K_v:
                t_ind +=1
                if t_ind >= len(THEMES):
                    t_ind = 0
                SETTED_TILE_COLOR, BUTTON_COLOR, SP_TILE_COLOR, FREE_TILE_COLOR, NORM_COLOR, TEXT_COLOR, SCREEN_COLOR, TIMELINE_COLOR, FIRST_PLAYER_COLOR, SECOND_PLAYER_COLOR = THEMES[t_ind]

            elif event.key == pygame.K_s:
                if timeline.current_player.num_special_tiles >0:
                    tile = Tile(0,0,0,[[True]])

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x_mouse, y_mouse = pygame.mouse.get_pos()
            column = x_mouse//(margin+widht)
            row = y_mouse//(margin+height)
            if timeline.current_player == player_2:
                column -= 11  # сдвижка, чтобы перейти на другое поле
            tile.get_all_configurations()
            tile_conf = tile.get_current_configuration()
            if timeline.current_player.players_field.is_placing_tile_possible(tile_conf, column, row):
                if timeline.current_player.num_buttons >= tile.price:
                    timeline.current_player.players_field.place_tile(tile_conf, column, row)
                    if tile.time ==0 and tile.price == 0 and tile.income == 0:
                        timeline.current_player.num_special_tiles -=1
                    time_add = tile.time
                    timeline.move(time_add)
                    income = timeline.buttons_income(time_add)
                    timeline.current_player.num_buttons -= tile.price
                    timeline.special_tiles(time_add)
                    common_tiles = common_tiles[ind+1:]
                    tile = common_tiles[0]
                    ind = 0
                    is_bonus = timeline.current_player.players_field.has_field_7x7_square()
                    if is_bonus:
                        timeline.current_player.is_bonus = True
                    timeline.whose_turn()
    if timeline.is_game_end():
        score_1 = count_scores(player_1)
        score_2 = count_scores(player_2)
        if score_1 > score_2:
            player_n = player_1.name
        elif score_2 > score_1:
            player_n = player_2.name
        else:
            player_n = 'Friendship'
        break


            #field.board[row][column] ^= 1

    keystate = pygame.key.get_pressed()
    if not keystate[pygame.K_h]:
#  draw a field
        for row in range(9):
            for col in range(9):
                if timeline.first_player.players_field.board[row][col]:
                    color = SETTED_TILE_COLOR
                else:
                    color = NORM_COLOR
                x = col*widht + (col+1)*margin
                y = row*height + (row+1)*margin
                pygame.draw.rect(screen,color, (x,y,widht, height))

        for row in range(9):
            for col in range(9):
                if timeline.second_player.players_field.board[row][col]:
                    color = SETTED_TILE_COLOR
                else:
                    color = NORM_COLOR
                x = col*widht + (col+1)*margin
                y = row*height + (row+1)*margin
                pygame.draw.rect(screen,color, (495+x,y,widht, height))
        
#draw a tile
    x_mouse, y_mouse = pygame.mouse.get_pos()
    column = x_mouse//(margin+widht)
    row = y_mouse//(margin+height)
    #print(column, row)
    tile.get_all_configurations()
    t_conf = tile.get_current_configuration()
    for t_row in range(len(t_conf)):
        for t_col in range(len(t_conf[0])):
            if t_conf[t_row][t_col] == True:
                x = (column+t_col)*(widht+margin) + margin
                y = (row+t_row)*(height+margin) + margin
                pygame.draw.rect(screen,FREE_TILE_COLOR,(x,y,widht,height))

# draw tips (if h is pressed)
    draw_game_tip()
    
#draw timeline (if t is pressed)
    first_player = timeline.first_player.time_coords
    second_player = timeline.second_player.time_coords
    draw_timeline(special_tiles_coords, button_income_coords, first_player, second_player)
    
    pygame.display.update()

screen.fill(SCREEN_COLOR)
textSurf, TextRect = text_objects(f'{player_n} won', GAME_FONT)
screen.blit(textSurf, (400,200))
pygame.display.update()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit(0)
    
