import pygame
import math
import random

# Initialise the pygame module
pygame.init()

# Declaring all the constants
FPS = 60
SCORE = [0]

WIDTH, HEIGHT = 800, 800
ROWS = 4
COLS = 4

RECT_HEIGHT = HEIGHT // ROWS
RECT_WIDTH = WIDTH // COLS

OUTLINE_COLOR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205, 192, 180)
FONT_COLOR = (119, 110, 101)

FONT = pygame.font.SysFont("comicsans", 60, bold=True)
MOVE_VEL = 20  # 20 pixels per second

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")

# Drawing

class Tile:
    COLORS = [
        (237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 115),
        (237, 204, 99),
        (236, 202, 80),
    ]

    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT

    def score(self):
        SCORE[0] = SCORE[0] + self.value

    def get_color(self):
        color_index = int(math.log2(self.value)) - 1
        color = self.COLORS[color_index]
        return color

    def draw(self, window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))

        text = FONT.render(str(self.value), 1, FONT_COLOR)
        window.blit(
            text,
            (
                self.x + (RECT_WIDTH / 2 - text.get_width() / 2),
                self.y + (RECT_HEIGHT / 2 - text.get_height() / 2),
            ),
        )

    def set_pos(self, ceil=False):
        if ceil:
            self.row = math.ceil(self.y / RECT_HEIGHT)
            self.col = math.ceil(self.x / RECT_WIDTH)
        else:
            self.row = math.floor(self.y / RECT_HEIGHT)
            self.col = math.floor(self.x / RECT_WIDTH)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]


def draw_grid(window):
    # 0th row need not be drawn again since it is already drawn by rectangle
    for row in range(1, ROWS):
        y = row * RECT_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)

    for col in range(1, COLS):
        x = col * RECT_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)

    pygame.draw.rect(window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)


def draw(window, tiles):
    window.fill(BACKGROUND_COLOR)

    for tile in tiles.values():
        tile.draw(window)

    draw_grid(window)

    score_text = FONT.render(f"Score: {SCORE[0]}", 1, FONT_COLOR)
    window.blit(score_text, (20, 5))
    pygame.display.update()


def draw_game_over_text(window):
  text_surface = FONT.render("Game Over", True, (240, 0, 0, 0.5))
  text_x = (window.get_width() - text_surface.get_width()) // 2
  text_y = (window.get_height() - text_surface.get_height()) // 2
  window.blit(text_surface, (text_x, text_y))


def get_random_pos(tiles):
    row = None
    col = None
    while True:
        row = random.randrange(0, ROWS)
        col = random.randrange(0, COLS)

        if f"{row}{col}" not in tiles:
            break

    return row, col


def move_tiles(window, tiles, clock, direction):
    updated = True
    blocks = set()

    if direction == "left":
        sort_fun = lambda x: x.col
        reverse = False  # sort in reverse order or not
        delta = (-MOVE_VEL, 0)  # by how much each tile is gonna move in this movement function
        boundary_check = lambda tile: tile.col == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col - 1}")
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.x > next_tile.x + RECT_WIDTH + MOVE_VEL
        )
        ceil = True

    elif direction == "right":
        sort_fun = lambda x: x.col
        reverse = True  # sort in reverse order or not
        delta = (MOVE_VEL, 0)  # by how much each tile is gonna move in this movement function
        boundary_check = lambda tile: tile.col == COLS-1
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col + 1}")
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.x + RECT_WIDTH + MOVE_VEL < next_tile.x
        )
        ceil = False

    elif direction == "up":
        sort_fun = lambda x: x.row
        reverse = False  # sort in reverse order or not
        delta = (0, -MOVE_VEL)  # by how much each tile is gonna move in this movement function
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row - 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.y > next_tile.y + RECT_HEIGHT + MOVE_VEL
        )
        ceil = True

    elif direction == "down":
        sort_fun = lambda x: x.row
        reverse = True  # sort in reverse order or not
        delta = (0, MOVE_VEL)  # by how much each tile is gonna move in this movement function
        boundary_check = lambda tile: tile.row == ROWS-1
        get_next_tile = lambda tile: tiles.get(f"{tile.row + 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - MOVE_VEL
        move_check = (
            lambda tile, next_tile: next_tile.y + RECT_HEIGHT + MOVE_VEL < next_tile.y
        )
        ceil = False

    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_fun, reverse=reverse)

        for i, tile in enumerate(sorted_tiles):
            if boundary_check(tile):
                continue
            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move(delta)
            elif (
                tile.value == next_tile.value
                and tile not in blocks
                and next_tile not in blocks
            ):
                if merge_check(tile, next_tile):
                    tile.move(delta)
                else:
                    next_tile.value *= 2
                    next_tile.score()
                    sorted_tiles.pop(i)
                    blocks.add(next_tile)
            elif move_check(tile, next_tile):
                tile.move(delta)
            else:
                continue
            
            tile.set_pos(ceil)
            updated = True

        update_tile(window, tiles, sorted_tiles)

    return end_move(tiles)


def end_move(tiles):
    if len(tiles) == ROWS*COLS:
        return 'LOST'
    
    row, col = get_random_pos(tiles)
    tiles[f"{row}{col}"] = Tile(random.choice([2,4]), row, col)
    return 'CONTINUE'


def update_tile(window, tiles, sorted_tiles):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile

    draw(window, tiles)


def generate_tiles():
    tiles = {}
    for _ in range(2):
        try:
            row, col = get_random_pos(tiles)
            tiles[f"{row}{col}"] = Tile(2, row, col)
        except Exception as e:
            print(f"Error generating tiles {e}")
    return tiles


def main(window):
    clock = pygame.time.Clock()
    run = True

    tiles = generate_tiles()

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x = move_tiles(window, tiles, clock, 'left')
                elif event.key == pygame.K_RIGHT:
                    x = move_tiles(window, tiles, clock, 'right')

                elif event.key == pygame.K_UP:
                    x = move_tiles(window, tiles, clock, 'up')
                elif event.key == pygame.K_DOWN:
                    x = move_tiles(window, tiles, clock, 'down')
                
                if x == 'LOST':
                    overlay_surface = pygame.Surface(window.get_size())
                    overlay_surface.set_alpha(128)
                    window.blit(overlay_surface, (0, 0))
                    draw_game_over_text(window)
                    pygame.display.update()
                    
                    pygame.time.wait(2000)

                    tiles = generate_tiles()
                    SCORE[0] = 0

        draw(window, tiles)
        pygame.display.update()


    pygame.quit()


if __name__ == "__main__":
    main(WINDOW)