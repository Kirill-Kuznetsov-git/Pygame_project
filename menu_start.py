import sys
import game
from PyQt5.QtWidgets import *


def terminate():
    sys.exit()


res = 0

# изначальное меню с двумя кнопками и управлением


class Example(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(300, 200, 500, 200)
        self.setWindowTitle('Game Меню')

        self.start = QPushButton('ЗАПУСТИТЬ ИГРУ', self)
        self.start.resize(100, 30)
        self.start.move(40, 30)
        self.start.clicked.connect(self.st0)

        self.end = QPushButton('ВЫХОД', self)
        self.end.resize(100, 30)
        self.end.move(40, 70)
        self.end.clicked.connect(self.exnm)

        self.control = QLabel(self)
        self.control.move(150, 30)
        self.control.setText('Управление:\nZ-выстрел\nSpace-Прыжок\nСтрелки влево и вправо- ходить влево и вправо\nВсего три жизни\nЗелье - бессмертие')

    def st0(self):
        global level
        i, okBtnPressed = QInputDialog.getItem(self, "Выбор",
                                               "Выберите уровень:",
                                               ("1 уровень", "2 уровень"),
                                               0, False)
        if okBtnPressed:
            level = int(i.split(' ')[0])
            self.st()

    def st(self):
        global game_next
        global level
        game_next = 1
        self.close()

    def exnm(self):
        sys.exit()


game_next = 0
level = 1

# данная функция вызывается в game если игрок умер


def start():
    global game_next
    game_next = 0
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    app.exec()
    if game_next == 1:
        game.main(level)
    sys.exit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    app.exec()
    if game_next == 1:
        res = 1
        game.main(level)
        game_next = 0
    sys.exit()
