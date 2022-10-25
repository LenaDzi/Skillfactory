from random import randint
# я не смогла создать такую игру, так как у меня не достаточно опыта, но постаралась описать процесс

class Dot:  # класс точек на поле по координатам
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):  # функция для сравнения точек
        return self.x == other.x and self.y == other.y

    def __repr__(self):  # функция с методом для предоставления текстового образа объекта
        return f"({self.x}, {self.y})"


class BoardException(Exception):  # общий класс исключений которые содержит исключения
    pass


class BoardOutException(BoardException):  # исключение при выходе из заданного диапазона
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):  # исключение если есть совпадения в выбранных точках
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):  # исключение для размещения кораблей
    pass


class Ship:  # описание коробля
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property  # метод который вычислчяет свойство корабля
    def dots(self):
        ship_dots = []
        for i in range(self.l):  # цикл для определения все точек корабля
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))  # добавляет точки корабля

        return ship_dots

    def shooten(self, shot):  # проверка на поподание
        return shot in self.dots


class Board:  # класс описывающий слздание игрового поля
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0  # переменная количества пораженнх кораблей

        self.field = [["O"] * size for _ in range(size)]  # создание пустого игрового поля с "О"

        self.busy = []  # в данной переменной будут хранится занятые точки
        self.ships = []  # список кораблей доски

    def add_ship(self, ship):  # размещение корабля

        for d in ship.dots:
            if self.out(d) or d in self.busy: # проверяем, что точки корабля не выходят за границы поля и что они не заняты
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■" #в точках карабля ставим квадрат
            self.busy.append(d) #записвываем точки в список зянятых

        self.ships.append(ship)  # список собственных кораблей
        self.contour(ship)  # делаем контур

    def contour(self, ship, verb=False):  # определение контура корабля
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)  # объявления все точек вокруг точки на которой находимся
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy: #если точки не выходят за границы и не заняты
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur) #добавлям точки в список занятых и ставим точку

    def __str__(self):  # вывод размеченного игрового поля и кораблей на доску
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:  # параметр отвечающий за свойства скрывать корабли или нет
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (
                    0 <= d.y < self.size))  # метод которым проверяем находится ли точка за пределами поля

    def shot(self, d): # выстрел
        if self.out(d): # проверка
            raise BoardOutException() # если тока выходит за границы применяем исключение

        if d in self.busy:
            raise BoardUsedException() #  если точка занята применяем исключение

        self.busy.append(d) # говорим, что точка занята

        for ship in self.ships: # проверяем точки корабля на совпадение с выстрелом
            if d in ship.dots: # если корабль был паражен
                ship.lives -= 1 # уменьшаем количесто точек корабля на 1
                self.field[d.x][d.y] = "X" #  меняем с точки на Х (корабль поражен)
                if ship.lives == 0: # если у корабля закончились жизни
                    self.count += 1 # к счетчику плюсуем уничтоженные корабли
                    self.contour(ship, verb=True) # обводим по контуру
                    print("Корабль уничтожен!") # выводим на экран
                    return False
                else:
                    print("Корабль ранен!") # если корабль не уничтожен выводим сообщение
                    return True # повторяем ход

        self.field[d.x][d.y] = "." # если был промах ставим точку
        print("Мимо!")
        return False

    def begin(self): # начало игры
        self.busy = [] # обнуление списка


class Player: # класс игрока
    def __init__(self, board, enemy): #  2 доски
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self): # просим сделать выстрел
        while True: # бесконечный цикл
            try:
                target = self.ask()
                repeat = self.enemy.shot(target) # если выстрел пршел успешно
                return repeat # просим повторить выстел еще раз
            except BoardException as e: # если выстрел неудачный и вызвал исключение
                print(e) # мы его печатаем и цикл продолжается


class AI(Player): # ходит программа
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5)) # возвращает случайное целое в заданных пределах
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player): # ход человека
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split() # ввести координаты

            if len(cords) != 2:
                print(" Введите 2 координаты! ") # проверка на количество координат
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):# если указали не числовые значения
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1) # вернем точку за вычетом еденицы


class Game: # класс игра
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board() #создаем доску для игрока
        co = self.random_board() #создаем доску для компьютера
        co.hid = True # скрываем корабли до компьютера

        self.ai = AI(co, pl) #создаем игрока компьютер
        self.us = User(pl, co) # создаем игрока пользователь

    def random_board(self):
        board = None
        while board is None: # в бесконечном цикле создаем доску
            board = self.random_place()
        return board # когда цикл закончится вернем уже заполненную доску

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1] # список длин кораблей
        board = Board(size=self.size)
        attempts = 0 # количество попыток (выстрелов)
        for l in lens: # каждый корабль
            while True: # будем ставить на доску в бесконечном цикле
                attempts += 1
                if attempts > 2000: # если количество выстрелов превысит 2000, вернуть пустую доску
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try: # когда корабли встали
                    board.add_ship(ship)
                    break # оканчиваем цикл
                except BoardWrongShipException: # если выбрасывает исключение повторяем все сначала
                    pass
        board.begin() # возвращаем доску с кораблями
        return board

    def greet(self): # вызов приветствия
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0 #номер хода
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0: # если номер хода четный - ходит пользователь
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat: # повтор хода если было попадание
                num -= 1

            if self.ai.board.count == 7: #если все 7 кораблей компьютера уничтожены
                self.print_boards()
                print("-" * 20)
                print("Пользователь выиграл!") #выводим на экран
                break

            if self.us.board.count == 7:  #если все 7 кораблей пользователя уничтожены
                self.print_boards()
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self): # совмещает все блоки и запускает программу
        self.greet()
        self.loop()


g = Game()
g.start()