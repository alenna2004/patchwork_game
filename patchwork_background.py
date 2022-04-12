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
        if self.first_player.time_coords >= (self.num_cells - 1) and self.second_player.time_coords >= (self.num_cells - 1):
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

