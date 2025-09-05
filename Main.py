import pygame
import random
from collections import deque

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

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700
TILE_SIZE = 100
GRID_WIDTH = 6
GRID_HEIGHT = 6

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

# Lógica de geração de Quebra-Cabeça 
def generate_final_puzzle(screen, font, min_solution_moves=10):
    loading_text = font.render('Gerando nível difícil...', True, BLACK)
    text_rect = loading_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))

    other_blocks_prototypes = [
        {'width': 1, 'height': 3, 'color': ORANGE}, {'width': 2, 'height': 1, 'color': YELLOW},
        {'width': 1, 'height': 2, 'color': GREEN},  {'width': 2, 'height': 1, 'color': BLUE},
        {'width': 1, 'height': 3, 'color': PURPLE}, {'width': 2, 'height': 1, 'color': CYAN},
        {'width': 2, 'height': 1, 'color': PINK}
    ]

    while True:
        screen.fill(WHITE)
        screen.blit(loading_text, text_rect)
        pygame.display.flip()
        pygame.event.pump()

        blocks = []
        start_y = random.choice([0, 1])
        red_block = Block(x=1, y=start_y, width=1, height=2, color=RED, is_main_block=True)
        blocks.append(red_block)

        possible_positions = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)]
        random.shuffle(possible_positions)
        occupied_cells = {(1, start_y), (1, start_y + 1)}
        
        for proto in other_blocks_prototypes:
            placed = False
            for x, y in possible_positions:
                new_rect = pygame.Rect(x, y, proto['width'], proto['height'])
                if new_rect.right > GRID_WIDTH or new_rect.bottom > GRID_HEIGHT:
                    continue
                collides = False
                for i in range(new_rect.width):
                    for j in range(new_rect.height):
                        if (x + i, y + j) in occupied_cells:
                            collides = True
                            break
                    if collides: break
                if not collides:
                    blocks.append(Block(x, y, proto['width'], proto['height'], proto['color']))
                    for i in range(new_rect.width):
                        for j in range(new_rect.height):
                            occupied_cells.add((x + i, y + j))
                    placed = True
                    break
            if not placed: break
        
        if len(blocks) != len(other_blocks_prototypes) + 1:
            continue
        
        solution = solve_puzzle(blocks, silent=True)
        if solution and len(solution) >= min_solution_moves:
            print(f"Nível encontrado com {len(solution)} movimentos!")
            return blocks

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Rush Hour Desafio Final")
    
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 40)

    blocks = generate_final_puzzle(screen, small_font, min_solution_moves=10)
    
    dragging_block, mouse_start_pos, block_start_pos = None, None, None
    game_won = False
    new_game_button = Button(SCREEN_WIDTH // 2 - 100, 620, 200, 60, "Nova Partida")
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s and not game_won:
                    print("Solver ativado...")
                    solution = solve_puzzle(blocks)
                    if solution:
                        print(f"\n--- SOLUÇÃO MÍNIMA: {len(solution)} MOVIMENTOS ---")
                        for i, move in enumerate(solution):
                            print(f"{i+1}. {move}")
                        print("------------------------------------------")

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if new_game_button.is_clicked(event.pos):
                        blocks = generate_final_puzzle(screen, small_font, min_solution_moves=10)
                        game_won, dragging_block = False, None
                        continue
                    if not game_won:
                        grid_x, grid_y = event.pos[0] // TILE_SIZE, event.pos[1] // TILE_SIZE
                        block = get_block_at(grid_x, grid_y, blocks)
                        if block:
                            dragging_block, mouse_start_pos, block_start_pos = block, event.pos, (block.x, block.y)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging_block = None

            if event.type == pygame.MOUSEMOTION:
                if dragging_block and not game_won:
                    mouse_x, mouse_y = event.pos
                    dx, dy = mouse_x - mouse_start_pos[0], mouse_y - mouse_start_pos[1]
                    target_x, target_y = block_start_pos
                    if dragging_block.height == 1:
                        target_x += round(dx / TILE_SIZE)
                    elif dragging_block.width == 1:
                        target_y += round(dy / TILE_SIZE)
                    if (target_x, target_y) != (dragging_block.x, dragging_block.y):
                        if is_move_valid(dragging_block, target_x, target_y, blocks):
                            dragging_block.x, dragging_block.y = target_x, target_y
                            mouse_start_pos, block_start_pos = event.pos, (dragging_block.x, dragging_block.y)
                            
                            main_block = next(b for b in blocks if b.is_main_block)
                            if main_block.y == GRID_HEIGHT - main_block.height:
                                print("Você venceu!")
                                game_won = True
        
        screen.fill(WHITE)
        draw_exit_zone(screen)
        draw_grid(screen)
        for block in blocks:
            block.draw(screen)
        
        new_game_button.draw(screen)
        if game_won:
            text = font.render('VOCÊ VENCEU!', True, BLACK, (200, 255, 200))
            text_rect = text.get_rect(center=(SCREEN_WIDTH/2, (GRID_HEIGHT * TILE_SIZE)/2))
            screen.blit(text, text_rect)
            
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == '__main__':
    main()
