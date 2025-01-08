import pygame
import random

pygame.init()

# Дефолт настройки
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BLOCK_DIMENSION = 20
COLUMNS = int(WINDOW_WIDTH / BLOCK_DIMENSION)
ROWS = int(WINDOW_HEIGHT / BLOCK_DIMENSION)
MOVEMENT_SPEED = 0.1

# Задаю цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
BEZHEVIY = (245, 245, 220)

# Палитра цветов для фигур
COLOR_PALETTE = [CYAN, BLUE, MAGENTA, YELLOW, GREEN, RED]

# Все возможные фигуры
SHAPE_TEMPLATES = [
    [[1, 1, 1, 1]],  # Фигура "I"
    [[1, 1, 1], [0, 1, 0]],  # Фигура "T"
    [[1, 1, 1], [1, 0, 0]],  # Фигура "L"
    [[1, 1, 1], [0, 0, 1]],  # Фигура "J"
    [[1, 1], [1, 1]],  # Фигура "O"
    [[0, 1, 1], [1, 1, 0]],  # Фигура "S"
    [[1, 1, 0], [0, 1, 1]]  # Фигура "Z"
]

class Tetromino:
    def __init__(self, pos_x, pos_y, shape_matrix):
        self.x = pos_x # Начальная позиция по иксу
        self.y = pos_y # Начальная позиция по игрику

        self.shape = [
            shape_matrix,
            self.rotate_matrix(shape_matrix),
            self.rotate_matrix(self.rotate_matrix(shape_matrix)),
            self.rotate_matrix(self.rotate_matrix(self.rotate_matrix(shape_matrix)))
        ] # Возможные положения фигуры

        self.color = random.choice(COLOR_PALETTE) # случайный выбор цвета для фигуры
        self.rotation_state = 0 # начальное состояние фигуры

    # вращение фигуры
    def rotate(self):
        self.rotation_state = (self.rotation_state + 1) % len(self.shape)

    # получение изображения фигуры
    def get_image(self):
        return self.shape[self.rotation_state]

    # поворот на 90 градусов
    @staticmethod
    def rotate_matrix(matrix):
        return [list(row) for row in zip(*matrix[::-1])]


class TetrisGame:
    def __init__(self, screen):
        self.screen = screen    # создание экрана
        self.grid = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]  # сетка игры
        self.current_piece = self.generate_new_piece() # текущая фигура
        self.next_piece = self.generate_new_piece() #следующая фигура
        self.score = 0 # очки

        self.is_game_over = False # конец игры
        self.move_dx = 0 # перемещение по иксу
        self.move_dy = 0 # перемещение по игрику

    @staticmethod
    def generate_new_piece():
        return Tetromino(COLUMNS // 2 - 2, 0, random.choice(SHAPE_TEMPLATES))

    def check_collision(self, offset_x=0, offset_y=0):
        for y, row in enumerate(self.current_piece.get_image()):
            for x, cell in enumerate(row):
                if cell:
                    if (x + self.current_piece.x + offset_x < 0 or
                            x + self.current_piece.x >= COLUMNS or
                            y + self.current_piece.y + offset_y >= ROWS or
                            self.grid[y + self.current_piece.y + offset_y][x + self.current_piece.x + offset_x] != BLACK):
                        return True

        return False

    def lock_piece(self):
        for y, row in enumerate(self.current_piece.get_image()):
            for x, cell in enumerate(row):
                if cell:
                    grid_y = y + self.current_piece.y
                    grid_x = x + self.current_piece.x
                    if 0 <= grid_y < ROWS and 0 <= grid_x < COLUMNS:
                        self.grid[grid_y][grid_x] = self.current_piece.color
        self.clear_filled_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.generate_new_piece()
        if self.check_collision():
            self.is_game_over = True

    def clear_filled_lines(self):
        lines_to_clear = [i for i, row in enumerate(self.grid) if all(cell != BLACK for cell in row)]
        for i in lines_to_clear:
            del self.grid[i]
            self.grid.insert(0, [BLACK for _ in range(COLUMNS)])
        self.score += 100

    def move_piece(self, delta_x):
        if not self.check_collision(delta_x, 0):
            self.current_piece.x += 1

    def drop_piece(self):
        if not self.check_collision(0, 1):
            self.current_piece.y += 1
        else:
            self.lock_piece()

    def rotate_piece(self):
        self.current_piece.rotate()
        if self.check_collision():
            self.current_piece.rotate()
            self.current_piece.rotate()
            self.current_piece.rotate()

    def draw_grid(self):
        for y in range(ROWS):
            for x in range(COLUMNS):
                pygame.draw.rect(self.screen, GRAY, (x * BLOCK_DIMENSION, y * BLOCK_DIMENSION, BLOCK_DIMENSION, BLOCK_DIMENSION), 1)
                if self.grid[y][x] != BLACK:
                    pygame.draw.rect(self.screen, self.grid[y][x],
                                     (x * BLOCK_DIMENSION, y * BLOCK_DIMENSION, BLOCK_DIMENSION, BLOCK_DIMENSION))


    def draw_piece(self, piece):
        for y, row in enumerate(piece.get_image()):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        self.screen,
                        piece.color,
                        (
                            (x + piece.x) * BLOCK_DIMENSION,
                            (y + piece.y) * BLOCK_DIMENSION,
                            BLOCK_DIMENSION,
                            BLOCK_DIMENSION,
                        ),
                    )

    def draw_next_piece(self):
        for y, row in enumerate(self.next_piece.get_image()):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        self.screen,
                        self.next_piece.color,
                        (
                            (x + COLUMNS + 1) * BLOCK_DIMENSION,
                            (y + 1) * BLOCK_DIMENSION,
                            BLOCK_DIMENSION,
                            BLOCK_DIMENSION,
                        ),
                    )

    def render(self):
        self.screen.fill(BLACK)
        self.draw_grid()
        self.draw_piece(self.current_piece)
        self.draw_next_piece()
        font = pygame.font.SysFont('Arial', 25)
        score_text = font.render(f'Счет: {self.score}', True, WHITE)
        self.screen.blit(score_text, (10, 10))
        pygame.display.update()

    def update_game_status(self):
        if not self.is_game_over:
            self.drop_piece()
        else:
            font = pygame.font.SysFont("Helvetica", 50)
            game_over_text = font.render("Игра окончена", True, BEZHEVIY)
            self.screen.blit(
                game_over_text,
                (
                    WINDOW_WIDTH // 2 - game_over_text.get_width() // 2,
                    WINDOW_HEIGHT // 2 - game_over_text.get_height() // 2 - WINDOW_HEIGHT // 8,
                ),
            )

            pygame.display.update()
            pygame.time.wait(3000)
            pygame.quit()
            exit()


def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH + 6 * BLOCK_DIMENSION, WINDOW_HEIGHT))
    pygame.display.set_caption("Tetris")

    clock = pygame.time.Clock()
    game = TetrisGame(screen)
    running = True
    key_pressed = set()
    fall_speed = 500
    last_fall_time = pygame.time.get_ticks()

    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key in {pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT}:
                    key_pressed.add(event.key)
            if event.type == pygame.KEYUP:
                if event.key in {pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT}:
                    key_pressed.discard(event.key)

        if pygame.K_LEFT in key_pressed:
            game.move_piece(-1)
        if pygame.K_RIGHT in key_pressed:
            game.move_piece(1)
        if pygame.K_DOWN in key_pressed:
            game.move_piece(0)
            game.drop_piece()
        if pygame.K_UP in key_pressed:
            game.rotate_piece()
        if current_time - last_fall_time > fall_speed:
            game.drop_piece()
            last_fall_time = current_time

        game.render()

        game.update_game_status()

        clock.tick(10)

main()