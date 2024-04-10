from datetime import datetime
import pygame as pg
from random import choice, randint
from typing import Optional


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
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


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
        raise NotImplementedError(
            f'Определите метод draw в {(self.__class__.__name__)}.')

    def draw_rectangle(self, position: tuple[int, int]) -> None:
        """Метод для отрисовки прямоугольных объектов на игровом поле."""
        rect: pg.Rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)  # type: ignore
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


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

    def __init__(self,
                 position: Optional[tuple[int, int]] = None,
                 body_color: tuple[int, int, int] = APPLE_COLOR
                 ) -> None:
        self.body_color = body_color
        self.position = self.randomize_position()

    @staticmethod
    def randomize_position() -> tuple[int, int]:
        """
        Метод для установки случайного положения яблока на игровом поле.
        Возвращает кортеж с координатами яблока.
        """
        position: tuple[int, int] = (
            randint(0, GRID_WIDTH - 20) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 20) * GRID_SIZE,
        )
        return position

    def generate_new_apple(self) -> None:
        """Метод для генерации нового яблока на поле."""
        self.position = self.randomize_position()

    def draw(self) -> None:
        """Метод для отрисовки яблока на поле."""
        self.draw_rectangle(self.position)


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

    def __init__(self,
                 position: tuple[int, int] = DEFAULT_POSITION,
                 body_color: tuple[int, int, int] = SNAKE_COLOR
                 ) -> None:
        self.position = position
        self.reset(body_color=body_color)

    def update_direction(self, next_direction) -> None:
        """Метод для обновления направления движения змейки."""
        if next_direction:
            self.direction = next_direction
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
        head_position_x: int  # Определение излишнее, так как можно задать
        head_position_y: int  # сразу, но тогда не удастся указать тип.
        head_position_x, head_position_y = self.get_head_position()
        d_x: int = self.direction[0] * GRID_SIZE
        d_y: int = self.direction[1] * GRID_SIZE
        new_head_position: tuple[int, int] = (
            (head_position_x + d_x) % SCREEN_WIDTH,
            (head_position_y + d_y) % SCREEN_HEIGHT
        )
        self.positions.insert(0, new_head_position)
        self.last = self.positions.pop(-1)

    def draw(self) -> None:
        """Метод для отрисовки змейки на экране."""
        for position in self.positions[:-1]:
            self.draw_rectangle(position)

        # Отрисовка головы змейки
        self.draw_rectangle(self.get_head_position())

        # Затирание последнего сегмента
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self) -> tuple[int, int]:
        """Метод для получения позиции головы змейки."""
        return self.positions[0]

    def reset(self, position=DEFAULT_POSITION,
              body_color=SNAKE_COLOR,
              direction_fixed: bool = True) -> None:
        """
        Метод для сброса змейки в начальное состояние
        после столкновения с собой.
        """
        self.body_color = body_color
        self.positions = [position]
        self.length: int = 1
        if direction_fixed:
            self.direction: tuple[int, int] = RIGHT  # type: ignore
        else:
            self.direction = choice([RIGHT, LEFT, UP, DOWN])
        self.next_direction: Optional[tuple[int, int]] = None  # type: ignore
        self.last: Optional[tuple[int, int]] = None  # type: ignore


def handle_keys(game_object) -> None:
    """Функция для обработки нажатия клавиш для управления змейкой."""
    directions = {
        pg.K_UP: (UP, DOWN),
        pg.K_DOWN: (DOWN, UP),
        pg.K_LEFT: (LEFT, RIGHT),
        pg.K_RIGHT: (RIGHT, LEFT)
    }
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key in directions:
                new_direction, opposite_direction = directions[event.key]
                if game_object.direction != opposite_direction:
                    game_object.next_direction = new_direction


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
    pg.init()
    snake = Snake()
    apple = Apple()
    screen.fill(BOARD_BACKGROUND_COLOR)
    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction(snake.next_direction)
        snake.move()
        if snake.get_head_position() in snake.positions[1:]:
            now = datetime.now()
            short_datetime = now.strftime(" %d-%m-%Y %H:%M")
            with open('statistic.txt', 'a') as f:
                f.write(f'Игра:{short_datetime}, длина змейки {snake.length}.')
            snake.reset(direction_fixed=False)
            screen.fill(BOARD_BACKGROUND_COLOR)
        if snake.positions[0] == apple.position:
            snake.length += 1
            snake.positions.append(apple.position)
            apple.generate_new_apple()
            while True:  # Порядочные яблоки на змейках не вырастают.
                if apple.position in snake.positions:
                    apple.generate_new_apple()
                else:
                    break
        snake.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
