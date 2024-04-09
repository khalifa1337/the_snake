from random import choice, randint
from typing import Optional

import pygame

# Инициализация PyGame:
pygame.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Стандратная позиция объекта
DEFAULT_POSITION = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """
    Базовый класс игрового объекта,
    от которого наследуются другие игровые объекты.

    ...

    Атрибуты
    --------
    position: положение объекта на игровом поле
    body_color: цвет игрового объекта
    """

    def __init__(self,
                 position: tuple[int, int] = DEFAULT_POSITION,
                 body_color: Optional[tuple[int, int, int]] = None) -> None:
        self.body_color = body_color
        self.position = position

    def draw(self) -> None:
        """
        Абстрактный метод для отрисовки объекта на экране.
        Переопределяется в каждом дочернем классе.
        """
        pass


class Apple(GameObject):
    """
    Класс, описывающий объект "яблоко" и действия с ним.
    Наследуется от базового класса игрового объекта.

    ...

    Атрибуты
    --------
    body_color - цвет яблока
    position - положение яблока на игровом поле
    """

    def __init__(self) -> None:
        self.body_color = APPLE_COLOR
        self.position = Apple.randomize_position()
        super().__init__(self.position, self.body_color)

    @staticmethod
    def randomize_position() -> tuple[int, int]:
        """
        Метод для установки случайного положения яблока на игровом поле.
        Возвращает кортеж с координатами яблока.
        """
        position: tuple[int, int] = (randint(0, GRID_WIDTH - 20) * GRID_SIZE,
                                     randint(0, GRID_HEIGHT - 20) * GRID_SIZE,
                                     )
        return position

    def generate_new_apple(self):
        """Метод для генерации нового яблока на поле."""
        self.position = Apple.randomize_position()

    def draw(self) -> None:
        """Метод для отрисовки яблока на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)  # type: ignore
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """
    Класс, описывающий объект змейка, его поведение.

    ...

    Атрибуты
    --------
    body_color - цвет змейки
    position - изначальное положение змейки на игровом поле
    length - длина змейки
    direction - текущее направление змейки
    next_direction - последующее направление змейки
    last - координаты последнего элемента змейки
    """

    def __init__(self) -> None:
        self.body_color = SNAKE_COLOR
        self.positions = [DEFAULT_POSITION]
        super().__init__(self.positions[0], self.body_color)
        self.length: int = 1
        self.direction: tuple[int, int] = RIGHT
        self.next_direction: Optional[tuple[int, int]] = None
        self.last: Optional[tuple[int, int]] = None

    def update_direction(self) -> None:
        """Метод для обновления направления движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """
        Метод для обновления позиции змейки.
        Изначально задает направлению змейки значение последующего направления.
        Далее получаем координату "головы" змейки.
        Производим "движение".
        Если змейка встретилась сама с собой - сбрасываем игру.
        """
        if self.next_direction:
            self.direction = self.next_direction
        current_head_position: tuple[int, int] = self.get_head_position()
        d_x: int = self.direction[0] * GRID_SIZE
        d_y: int = self.direction[1] * GRID_SIZE
        new_head_position: tuple[int, int] = ((current_head_position[0] + d_x
                                               ) % SCREEN_WIDTH,
                                              (current_head_position[1] + d_y
                                               ) % SCREEN_HEIGHT)
        if new_head_position not in self.positions:
            self.positions.insert(0, new_head_position)
            self.last = self.positions.pop(-1)
        else:
            self.reset()

    def draw(self) -> None:
        """Метод для отрисовки змейки на экране."""
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)  # type: ignore
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)  # type: ignore
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self) -> tuple[int, int]:
        """Метод для получения позиции головы змейки."""
        return self.positions[0]

    def eat_apple(self, apple_coords) -> None:
        """Метод для увеличения змейки при поедании яблока."""
        self.length += 1
        self.positions.append(apple_coords)

    def reset(self) -> None:
        """
        Метод для сброса змейки в начальное состояние
        после столкновения с собой.
        """
        self.length = 1
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = choice([RIGHT, LEFT, UP, DOWN])
        screen.fill(BOARD_BACKGROUND_COLOR)


def handle_keys(game_object) -> None:
    """Функция для обработки нажатия клавиш для управления змейкой."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """
    Главная функция игры игры.
    Задаем параметр скорости игры.
    "Опрашиваем" действие ввода.
    Производим движение змейки.
    Если встретили яблоко - съедаем его.
        Генерируем новое яблоко вне змейки
    Отрисовываем игровые объекты и обновляем игровое поле.
    """
    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        if snake.positions[0] == apple.position:
            snake.eat_apple(apple.position)
            apple.generate_new_apple()
            while True:  # Порядочные яблоки на змейках не вырастают.
                if apple.position in snake.positions: 
                    apple.generate_new_apple()
                else:
                    break
        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
