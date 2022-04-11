import numpy as np
import copy

FIELD_HEIGHT = FIELD_WIDTH = 9
NUM_BUTTONS_AT_START = 2
RULES = 'потом допишем'

class Tile:
    def __init__(self, price, income, time, base_configuration):
        self.price = price
        self.income = income
        self.time = time
        self.base_configuration = base_configuration
        self.num_chosen_conf = 0
        self.all_configurations = []

    def get_all_configurations(self):
        all_configurations = []
        all_configurations.append(self.base_configuration)
        for i in range(1,4):
            new_conf = np.rot90(copy.deepcopy(self.base_configuration), k=i)
            #if new_conf not in all_configurations:
            all_configurations.append(new_conf)
        flipped_conf = np.flip(copy.deepcopy(self.base_configuration), axis=1)
        #if flipped_conf not in all_configurations:
        all_configurations.append(flipped_conf)
        for i in range(1,4):
            new_conf = np.rot90(copy.deepcopy(flipped_conf), k=i)
            #if new_conf not in all_configurations:
            all_configurations.append(new_conf)
        self.all_configurations = all_configurations
    
    def get_current_configuration(self):
        return self.all_configurations[self.num_chosen_conf]

    def choose_next_configuration(self):
        self.num_chosen_conf +=1
        max_ind = len(self.all_configurations)-1
        if self.num_chosen_conf > max_ind:
            self.num_chosen_conf = 0


class QuiltBoard:
    def __init__(self, board):
        self.board = board
        self.has_bonus = False
    
    def has_field_7x7_square(self):
        square = np.ones((7, 7), dtype=bool)
        for i in range(3):
            for j in range(3):
                board_part = self.board[i:i+7, j:j+7]
                if np.all(square & board_part):
                    return True
        return False
    
    def is_placing_tile_possible(self, tile_conf, x_from, y_from):
        empty_field = np.zeros((FIELD_HEIGHT, FIELD_WIDTH), dtype=bool)
        tile_height, tile_width = len(tile_conf), len(tile_conf[0])
        try:
            empty_field[y_from:y_from+tile_height, x_from:x_from+tile_width] = tile_conf
            return np.all(empty_field & self.board == False)
        except ValueError:
            return False
    
    def place_tile(self, tile_conf, x_from, y_from):
        tile_height, tile_width = len(tile_conf), len(tile_conf[0])
        stored_cells = []
        for i in range(y_from,y_from+tile_height):
            for j in range(x_from,x_from+tile_width):
                if self.board[i,j] == True:
                    stored_cells.append([i,j])
        self.board[y_from:y_from+tile_height, x_from:x_from+tile_width] = tile_conf
        for el in stored_cells:
            self.board[el[0], el[1]] = True
    
    def empty_cells_left(self):
        return np.count_nonzero(self.board)

class TimeLine:
    def __init__(self, num_cells, button_income_coords, special_tiles_coords, first_player, second_player):
        self.num_cells = num_cells
        self.button_income_coords = button_income_coords
        self.special_tiles_coords = special_tiles_coords
        self.first_player = first_player
        self.second_player = second_player
        self.current_player = self.first_player
    
    def move(self, step):
        self.current_player.time_coords+=step
    
    def buttons_income(self, step):
        if self.current_player == self.first_player:
            coord = self.first_player.time_coords
            indexes =[i for i in range(coord-step,coord)]
            for i in self.button_income_coords:
                if i in indexes:
                    self.first_player.num_buttons += self.first_player.income
        if self.current_player == self.second_player:
            coord = self.second_player.time_coords
            indexes =[i for i in range(coord-step,coord)]
            for i in self.button_income_coords:
                if i in indexes:
                    self.second_player.num_buttons += self.second_player.income
    
    def special_tiles(self, step):
        coord = self.current_player.time_coords
        indexes =[i for i in range(coord-step,coord)]
        inds_to_del = []
        for j in range(len(self.special_tiles_coords)):
            if self.special_tiles_coords[j] in indexes:
                self.first_player.num_special_tiles += 1
                inds_to_del.append(j)
        for i in inds_to_del:
            del self.special_tiles_coords[i]
    
    def whose_turn(self):
        if self.second_player.time_coords < self.first_player.time_coords:
            self.current_player = self.second_player
        else:
            self.current_player = self.first_player
    
    def is_game_end(self):
        if self.first_player.time_coords == (self.num_cells - 1) and self.second_player.time_coords == (self.num_cells - 1):
            return True
        return False

class Player:
    def __init__(self, players_field, name):
        self.name = name
        self.players_field = players_field
        self.num_buttons = NUM_BUTTONS_AT_START
        self.time_coords = 0
        self.num_special_tiles = 0
        self.income = 0
        self.is_bonus = False


def action_A(player_1, player_2, timeline):
    moving_player = timeline.current_player
    time_move = abs(player_1.time_coords - player_2.time_coords) +1
    moving_player.num_buttons += time_move
    timeline.move(time_move)
    timeline.buttons_income(time_move)
    timeline.special_tiles(time_move)
    print(f'''{moving_player.name} has {moving_player.num_buttons} buttons, 
    {moving_player.num_special_tiles} special tiles and stay in {moving_player.time_coords} in timeline''')


def action_B(player_1, player_2, timeline, tiles):
    if tiles[0].base_configuration != [[True]]:
        print(list(reversed([tile.base_configuration for tile in tiles])))
        print(f'Choose one from {len(tiles)}')
        tile_ind = (int(input()))*(-1)
        while tile_ind <-3 or tile_ind >-1:
            print(f'You can write only 1, 2 or 3')
            tile_ind = (int(input()))*(-1)
        chosen_tile = tiles[tile_ind]
        while chosen_tile.price > timeline.current_player.num_buttons:
            print('Choose another tile, you are too poor')
            tile_ind = (int(input()))*(-1)
            while tile_ind <-3 or tile_ind >-1:
                print(f'You can write only one from {len(tiles)}')
                tile_ind = (int(input()))*(-1)
            chosen_tile = tiles[tile_ind]
        time_add = chosen_tile.time
        chosen_tile.get_all_configurations()
        current_conf = chosen_tile.get_current_configuration()
        print(current_conf)
        print('To choose another configuration print next, to confirm configuration print ok')
        answer = str(input())
        while answer.lower() != 'ok':
            if answer.lower() == 'next':
                chosen_tile.choose_next_configuration()
                current_conf = chosen_tile.get_current_configuration()
                print(current_conf)
            answer = str(input())
    else:
        chosen_tile = tiles[0]
        current_conf = chosen_tile.base_configuration
    print('Choose the top left cell coordinates to place tile on a quilt board, First write x value, second write y value')
    x = int(input())
    y  = int(input())
    is_possible = timeline.current_player.players_field.is_placing_tile_possible(current_conf,x,y)
    while not is_possible:
        print('Choose another x and y')
        x = int(input())
        y = int(input())
        is_possible = timeline.current_player.players_field.is_placing_tile_possible(current_conf,x,y)
    timeline.current_player.players_field.place_tile(current_conf,x,y)
    if tiles[0].base_configuration != [[True]]:
        timeline.move(time_add)
        income = timeline.buttons_income(time_add)
        timeline.current_player.num_buttons -= chosen_tile.price
        timeline.special_tiles(time_add)
        print(f'''{timeline.current_player.name} has {timeline.current_player.num_buttons} buttons, 
        {timeline.current_player.num_special_tiles} special tiles and stay in {timeline.current_player.time_coords} in timeline''')
        return tile_ind


def count_scores(player):
    total_score = 0
    total_score += player.num_buttons
    if player.is_bonus:
        total_score += 7
    total_score -= 2*player.players_field.empty_cells_left()
    return total_score


def play(num_cells_timeline, button_income_coords, special_tiles_coords, tiles_list,first_player_name='One', second_player_name='Two'):
    '''На вход подается 
    количество клеток поля времени(число), 
    координаты пуговиц(лист чисел) и специальных кусочков(лист чисел), 
    а также список обычных кусочков(список списков(двумерный массив(базовая конфигурация), цена, доход, смещение по времени)) 
    и при желании имена первого и второго игрока в виде двух строк
    '''
    print(f'RULES:{RULES}')
    is_bonus = False
    common_tiles = []
    for tile in tiles_list:
        if len(tile) !=4:
            print(len(tile))
            raise ValueError('Tile must contain only base configuration, price, income and time in this order.')
        conf = tile[0]
        price = tile[1]
        income = tile[2]
        time = tile[3]
        common_tiles.append(Tile(price,income,time,conf))
    start_board = empty_field = np.zeros((FIELD_HEIGHT, FIELD_WIDTH), dtype=bool)
    q_board_1 = QuiltBoard(start_board)
    q_board_2 = QuiltBoard(start_board)
    player_1 = Player(q_board_1, first_player_name)
    player_2 = Player(q_board_2, second_player_name)
    timeline = TimeLine(num_cells_timeline, button_income_coords, special_tiles_coords, player_1, player_2)
    while not timeline.is_game_end():
        print(f'Player {timeline.current_player.name} choose action A or B. To make a choice print A or B in next line')
        action_type = str(input())
        if action_type.lower() == 'a':
            action_A(player_1, player_2, timeline)
        elif action_type.lower() == 'b':
            tile_ind = action_B(player_1, player_2, timeline, common_tiles[-3:])
            common_tiles = common_tiles[:tile_ind]
        else:
            raise ValueError('Unexpected action. You can write only A or B')
        if not is_bonus:
            is_bonus = timeline.current_player.players_field.has_field_7x7_square()
            if is_bonus:
                timeline.current_player.is_bonus = True
        timeline.whose_turn()
        timeline.is_game_end()
        if len(common_tiles) == 0:
            break
    timeline.current_player = player_1
    while player_1.num_special_tiles !=0:
        sp_tile  = Tile(0,0,0,[[True]])
        action_B(player_1, player_2, timeline, [sp_tile])
        player_1.num_special_tiles -= 1
    timeline.current_player = player_2
    while player_2.num_special_tiles !=0:
        sp_tile  = Tile(0,0,0,[[True]])
        action_B(player_1, player_2, timeline, [sp_tile])
        player_2.num_special_tiles -= 1
    score_1 = count_scores(player_1)
    score_2 = count_scores(player_2)
    if score_1 > score_2:
        print(f'{player_1.name} won')
    if score_1 < score_2:
        print(f'{player_2.name} won')
    if  score_1 == score_2:
        print('Friendship won')
