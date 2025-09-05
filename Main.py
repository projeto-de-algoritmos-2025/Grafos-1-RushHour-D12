import pygame
import random
from collections import deque

# --- Constantes ---
# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (211, 211, 211)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)
BUTTON_COLOR = (100, 200, 100)
BUTTON_TEXT_COLOR = (255, 255, 255)

# Dimensões
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700
TILE_SIZE = 100
GRID_WIDTH = 6
GRID_HEIGHT = 6

# --- Classes ---
class Block:
    def __init__(self, x, y, width, height, color, is_main_block=False):
        self.x, self.y, self.width, self.height, self.color, self.is_main_block = x, y, width, height, color, is_main_block
    
    def draw(self, surface):
        rect = pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, self.width * TILE_SIZE, self.height * TILE_SIZE)
        pygame.draw.rect(surface, self.color, rect)
        if self.is_main_block:
            pygame.draw.rect(surface, BLACK, rect, 2)

    def is_over(self, grid_x, grid_y):
        return (self.x <= grid_x < self.x + self.width and self.y <= grid_y < self.y + self.height)

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, 40)

    def draw(self, surface):
        pygame.draw.rect(surface, BUTTON_COLOR, self.rect)
        text_surf = self.font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# --- Funções Auxiliares ---
def draw_grid(surface):
    for x in range(0, GRID_WIDTH * TILE_SIZE + 1, TILE_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, GRID_HEIGHT * TILE_SIZE))
    for y in range(0, GRID_HEIGHT * TILE_SIZE + 1, TILE_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (GRID_WIDTH * TILE_SIZE, y))

def draw_exit_zone(surface):
    x_pos = 1
    y = GRID_HEIGHT * TILE_SIZE
    start_x, end_x = x_pos * TILE_SIZE, (x_pos + 1) * TILE_SIZE
    pygame.draw.line(surface, BLACK, (start_x, y), (end_x, y), 5)

def get_block_at(grid_x, grid_y, blocks):
    for block in blocks:
        if block.is_over(grid_x, grid_y):
            return block
    return None

def is_move_valid(moving_block, new_x, new_y, all_blocks):
    if not (0 <= new_x and new_x + moving_block.width <= GRID_WIDTH and
            0 <= new_y and new_y + moving_block.height <= GRID_HEIGHT):
        return False
    for other_block in all_blocks:
        if other_block is moving_block:
            continue
        if (new_x < other_block.x + other_block.width and
            new_x + moving_block.width > other_block.x and
            new_y < other_block.y + other_block.height and
            new_y + moving_block.height > other_block.y):
            return False
    return True

def blocks_to_state(blocks):
    return tuple(sorted((b.x, b.y, b.width, b.height, b.is_main_block) for b in blocks))

def solve_puzzle(initial_blocks, silent=False):
    initial_state = blocks_to_state(initial_blocks)
    main_block_props = next((b for b in initial_blocks if b.is_main_block), None)
    if not main_block_props:
        return None
    exit_x, exit_y = main_block_props.x, GRID_HEIGHT - main_block_props.height
    queue = deque([(initial_state, [])])
    visited = {initial_state}
    while queue:
        current_state_tuple, path = queue.popleft()
        for block_tuple in current_state_tuple:
            if block_tuple[4] and block_tuple[1] == exit_y and block_tuple[0] == exit_x:
                if not silent: print("Solução encontrada!")
                return path
        for i, block_tuple in enumerate(current_state_tuple):
            x, y, width, height, is_main = block_tuple
            possible_moves = []
            if height == 1:
                possible_moves.extend([(-1, 0, f"Bloco {i} H"), (1, 0, f"Bloco {i} H")])
            if width == 1:
                possible_moves.extend([(0, -1, f"Bloco {i} V"), (0, 1, f"Bloco {i} V")])
            for dx, dy, move_desc in possible_moves:
                new_x, new_y = x + dx, y + dy
                temp_blocks = [Block(b[0], b[1], b[2], b[3], b[4]) for b in current_state_tuple]
                if is_move_valid(temp_blocks[i], new_x, new_y, temp_blocks):
                    new_blocks_list = list(current_state_tuple)
                    new_blocks_list[i] = (new_x, new_y, width, height, is_main)
                    new_state = tuple(sorted(new_blocks_list))
                    if new_state not in visited:
                        visited.add(new_state)
                        new_path = path + [move_desc]
                        queue.append((new_state, new_path))
    if not silent:
        print("Nenhuma solução encontrada.")
    return None
