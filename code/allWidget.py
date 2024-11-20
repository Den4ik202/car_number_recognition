# импорт библиотеки для работы с визуализацией
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTableWidgetItem, QMessageBox)
from PyQt6.QtGui import QPixmap, QImage


# ----------------------------- экран со всеми номерами из базы данных ---------------------------------------
class WidgetAllNumber(QWidget):
    def __init__(self, result: tuple, pathProject: str) -> None:
        super().__init__()
        uic.loadUi(pathProject + r'\visualization\ui\number_in_bd.ui', self)  # Загружаем дизайн

        index = 0
        for all_elm in result:
            self.allNumbers.setRowCount(index + 1)
            self.allNumbers.setItem(index, 0, QTableWidgetItem(all_elm[1]))
            self.allNumbers.setItem(index, 1, QTableWidgetItem(all_elm[2]))
            self.allNumbers.setItem(index, 2, QTableWidgetItem(str(all_elm[3])))
            self.allNumbers.setItem(
                index, 3, QTableWidgetItem(str(all_elm[4])))
            self.allNumbers.setItem(
                index, 4, QTableWidgetItem(str(all_elm[5])))
            self.allNumbers.setItem(
                index, 5, QTableWidgetItem(all_elm[6]))
            index += 1


# ----------------------------------- экран с поисками номеров -------------------------------
class WidgetInfoNumber(QWidget):
    def __init__(self, smartGuard: object, pathProject: str) -> None:
        super().__init__()
        uic.loadUi(pathProject + r'\visualization\ui\inform_number.ui', self)  # Загружаем дизайн
        self.smartGuard = smartGuard
        self.infoNumber = ()  # информация о текущем номере
        
        self.pathProject = pathProject
        self.deleteNumber.clicked.connect(self.deletNumber)
        self.saveNumber.clicked.connect(self.addNumber)
        self.saveInform.clicked.connect(self.saveInforNumber)
        self.searchNumber.clicked.connect(self.displayNumber)
        self.openBDNumber.clicked.connect(self.openBD)

    # Создание диалогово окна
    def createErrorDialog(self, text: str) -> True:
        dlg = QMessageBox(self)
        dlg.setWindowTitle('')
        dlg.setText(text)
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
        dlg.setIcon(QMessageBox.Icon.Warning)
        button = dlg.exec()
        if button == QMessageBox.StandardButton.Ok:    # возращаем ошибку в виде диалогово окна
            return True

    # обработчик возможных ошибок
    def processingError(self) -> bool:
        if not (self.numberLable.text() and self.fioLable.text() and self.timeStopLable.text()):
            return self.createErrorDialog('Не все обязательные поля заполнены')

        if not self.timeStopLable.text().isdigit():        # поле не число
            return self.createErrorDialog(
                'Значение поля "Время остановки на парковке" должно быть число')

        if not self.blackListLable.text():
            self.blackListLable.setText('0')
        elif self.blackListLable.text() not in ['1', '0']:
            return self.createErrorDialog(
                'Значение поля "В черном ли листе" должно быть 1 или 0')

        if not self.numberParkingSpaiceLable.text():
            res = self.smartGuard.getParkingSpaces()
            if res == -1:            # свободных мест нет
                return self.createErrorDialog('Свободных мест нет')

            self.numberParkingSpaiceLable.setText(str(res))   
        elif not self.numberParkingSpaiceLable.text().isdigit():         # поле не число
            return self.createErrorDialog(
                'Значение поля "Номер парковочного места" должно быть число')
            
        return False

    # удаление номера
    def deletNumber(self) -> None:
        if self.processingError():
            return

        dlg = QMessageBox(self)
        dlg.setWindowTitle('')
        dlg.setText('Вы действительно хотите удалить номер?')
        dlg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()
        if button == QMessageBox.StandardButton.No:             # если нет, то завершаем функцию
            return

        self.smartGuard.deletNumdInBD(self.numberLable.text())

    # сохранение номера
    def addNumber(self) -> None:
        if self.processingError():
            return

        dlg = QMessageBox(self)
        dlg.setWindowTitle('')
        dlg.setText('Вы действительно хотите сохранить номер?')
        dlg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()
        if button == QMessageBox.StandardButton.No:             # если нет, то завершаем функцию
            return

        self.smartGuard.addNumdInBD((self.numberLable.text(),
                                     self.fioLable.text(),
                                     int(self.timeStopLable.text()),
                                     int(self.numberParkingSpaiceLable.text()),
                                     int(self.blackListLable.text()),
                                     self.otherInformationLable.text()))

    # сохранение изменений номера
    def saveInforNumber(self) -> None:
        if self.processingError():
            return

        dlg = QMessageBox(self)
        dlg.setWindowTitle('')
        dlg.setText('Вы действительно хотите сохранить изменения?')
        dlg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()
        if button == QMessageBox.StandardButton.No:             # если нет, то завершаем функцию
            return

        self.smartGuard.saveInforNumdInBD((self.numberLable.text(),
                                           self.fioLable.text(),
                                           int(self.timeStopLable.text()),
                                           int(self.numberParkingSpaiceLable.text()),
                                           int(self.blackListLable.text()),
                                           self.otherInformationLable.text()))

    # отображаем информацию номера
    def displayNumber(self) -> None:
        result = self.smartGuard.searchNumdInBD(
            self.textNumberLable.text().upper())
        if not result:

            # номер не был найден

            self.numberLable.setText('')
            self.fioLable.setText('')
            self.timeStopLable.setText('')
            self.numberParkingSpaiceLable.setText('')
            self.blackListLable.setText('')
            self.otherInformationLable.setText('')
            return
        self.numberLable.setText(result[0][1])
        self.fioLable.setText(result[0][2])
        self.timeStopLable.setText(str(result[0][3]))
        self.numberParkingSpaiceLable.setText(str(result[0][4]))
        self.blackListLable.setText(str(result[0][5]))
        self.otherInformationLable.setText(result[0][6])

    # открываем окошко со всеми номерами из базы данных
    def openBD(self) -> None:
        result = self.smartGuard.getAllNumberInBD()
        if not result:
            return self.createErrorDialog('В базе данных нет номеров')
        self.w = WidgetAllNumber(result, self.pathProject)
        self.w.show()


# ------------------------------------------------ главный экран --------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self, smartGuard: object, pathProject: str) -> None:
        super().__init__()
        uic.loadUi(pathProject + r'\visualization\ui\main_window.ui', self)  # Загружаем дизайн
        self.smartGuard = smartGuard
        self.pathProject = pathProject
        
        self.stateBarrier = False            # состояние шлагбаума
        self.searchNumber.clicked.connect(self.displayWidget)          # задаем функции для кнопок
        self.openBarrier.clicked.connect(self.openOrCloseBarrier)
        self.closeBarrier.clicked.connect(self.openOrCloseBarrier)
        self.deletText.clicked.connect(self.deletAllText)
        self.saveText.clicked.connect(self.saveAllText)
        
        self.synchronizationText()   # синхранизируем текст с заметками
        pixmap = QPixmap(pathProject + r'\visualization\img\close_barrier.png')            # указываем начальное фото для барьера 
        self.barrierLable.setPixmap(pixmap)
        
    # удаляем текст из заметок
    def deletAllText(self):
        with open(self.pathProject + r'\system files\TextEditor\text.txt', 'w', encoding='utf-8') as file:
            file.write('')
        self.editorTexting.setText('')
    
    # сохраняем текст
    def saveAllText(self):
        with open(self.pathProject + r'\system files\TextEditor\text.txt', 'w', encoding='utf-8') as file:
            file.write(self.editorTexting.toPlainText())
    
    # делаем синхронизацию с заметками
    def synchronizationText(self):
        with open(self.pathProject + r'\system files\TextEditor\text.txt', 'r', encoding='utf-8') as file:
            text = ''.join([line for line in file.readlines()])
        
        self.editorTexting.setText(text)
        
    # обновление картинки
    def updateImage(self, img) -> None:
        self.videoCature.setPixmap(self.convert_cv_qt(img))

    # конвертирование из OpenCV картинки в QPixmap
    def convert_cv_qt(self, cvImg) -> QPixmap:
        height, width, _ = cvImg.shape
        bytesPerLine = 3 * width
        qImg = QImage(cvImg.data, width, height, bytesPerLine,
                      QImage.Format.Format_RGB888)
        
        return QPixmap(qImg)

    # отображение виджета
    def displayWidget(self) -> None:
        self.w = WidgetInfoNumber(self.smartGuard, self.pathProject)
        self.w.show()

    # получение состояние шлагбаума
    def getStateBarrier(self) -> bool:
        return self.stateBarrier
    
    # открытие шлагбаума
    def openOrCloseBarrier(self, open=True) -> None:       # вызвать ф-ию от кнопки и от другой ф-ии
        button = self.sender()
        if button:                               # была нажата кнопка
            if button.text() == 'Открыть шлагбаум':
                pixmap = QPixmap(self.pathProject + r'\visualization\img\open_barrier.png') # сохраняем открытый шлагбаум
                self.stateBarrier = True
            else:
                pixmap = QPixmap(self.pathProject + r'\visualization\img\close_barrier.png')
                self.stateBarrier = False
                
        if open and not button:      # была вызванна ф-ей
            pixmap = QPixmap(self.pathProject + r'\visualization\img\open_barrier.png')
            self.stateBarrier = True
            
        elif not button:
            pixmap = QPixmap(self.pathProject + r'\visualization\img\close_barrier.png')
            self.stateBarrier = False
    
        self.barrierLable.setPixmap(pixmap)
    
    # отабрежение номеров на парковочных местах
    def displayNumberInParking(self, result: list):
        index = 0
        self.carParking.removeRow(0)
        for all_elm in result:
            self.carParking.setRowCount(index + 1)
            self.carParking.setItem(index, 0, QTableWidgetItem(all_elm[1]))
            self.carParking.setItem(index, 1, QTableWidgetItem(all_elm[2]))
            self.carParking.setItem(index, 2, QTableWidgetItem(all_elm[3]))
    
    # создание диалогового окна об ошибке с определением номера в бд
    def createDialogError(self, text: str) -> False:
        dlg = QMessageBox(self)
        dlg.setWindowTitle('')
        dlg.setText(text)
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
        dlg.setIcon(QMessageBox.Icon.Warning)
        button = dlg.exec()
        if button == QMessageBox.StandardButton.Ok:    # возращаем ошибку в виде диалогово окна
            return False
    
    
    # создание диалогового окна, впускать ли номер
    def displayDialogNumberInParking(self, infromNumber: list, number: str) -> bool:
        if not infromNumber:
            return self.createDialogError(f'{number} нет в базе данных')
        if infromNumber[0][5] == 1:
            return self.createDialogError(f'{number} находиться в черном списке')
        
        box = QMessageBox()
        box.setWindowTitle('Номер определился')
        box.setText(f'Пропустить номер {number}?')
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        openShlag = box.button(QMessageBox.StandardButton.Yes)
        openShlag.setText('Открыть шлагбаум')
        noOpenShlag = box.button(QMessageBox.StandardButton.No)
        noOpenShlag.setText('Не открывать шлагбаум')
        box.setIcon(QMessageBox.Icon.Question)
        box.exec()
        if box.clickedButton() == openShlag:
            return True
        return False