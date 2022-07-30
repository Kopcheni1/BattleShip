import time
from random import randint


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Это была попытка выстрела за игровую доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Хватит бить в одно место!"


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, bow, length, place):
        self.bow = bow
        self.length = length
        self.place = place
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.place == 0:
                cur_x += i

            elif self.place == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooted(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hidden=False, size=6):
        self.size = size
        self.hidden = hidden

        self.count = 0

        self.field = [["≈"] * size for _ in range(size)]

        self.busy_dots = []
        self.ships = []

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out_board(d) or d in self.busy_dots:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "▲"
            self.busy_dots.append(d)

        self.ships.append(ship)
        self.ship_contour(ship)

    def ship_contour(self, ship, cl=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out_board(cur)) and cur not in self.busy_dots:
                    if cl:
                        self.field[cur.x][cur.y] = "."
                    self.busy_dots.append(cur)

    def __str__(self):
        toc = ""
        toc += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            toc += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hidden:
            toc = toc.replace("▲", "≈")
        return toc

    def out_board(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out_board(d):
            raise BoardOutException()

        if d in self.busy_dots:
            raise BoardUsedException()

        self.busy_dots.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.ship_contour(ship, cl=True)
                    print("Корабль потоплен!")
                    return False
                else:
                    print("Мы попали, он ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("О нет, снаряд пролетел мимо!")
        return False

    def start(self):
        self.busy_dots = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход противника: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Время вашего хода: ").split()

            if len(cords) != 2:
                print(" Введите обе координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        user = self.random_board()
        comp = self.random_board()
        comp.hidden = True

        self.ai = AI(comp, user)
        self.us = User(user, comp)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for length in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), length, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.start()
        return board

    def hi(self):
        print(" Добро пожаловать ")
        print(" -----в игру----- ")
        print(" --Морской  бой-- ")
        print(" ---------------- ")

    def loop_board(self):
        print("-" * 20)
        print("Доска пользователя:")
        print(self.us.board)
        print("-" * 20)
        print("Доска компьютера:")
        print(self.ai.board)

    def loop(self):
        num = 0
        while True:
            self.loop_board()
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                time.sleep(3)
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def begin(self):
        self.hi()
        self.loop()


g = Game()
g.begin()