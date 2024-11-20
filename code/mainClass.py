import datetime        # для работы с датой и временем
import sqlite3         # для работы с SQLite
import cv2             # машиное зрение
from pytesseract import pytesseract  # распазнвоание текста на картинке

# -------------------- класс для распазнования автомобильного номера и работы с БД --------------------
class SmartGuard:
    def __init__(self, pathPytesser: str, pathProject: str, countParkingSpaces=100) -> None:
        self.number_plate_cascade = cv2.CascadeClassifier(pathProject +
            r'\system files\RecText\haarcascade_russian_plate_number.xml')  # подключение каскада

        # подключение модкля распазнования автомобильного номера
        pytesseract.tesseract_cmd = pathPytesser
        self.replayNumber = []            # хранение предыдущих номеров
        # количество парковочных мест на этаже
        self.countParkingSpaces = countParkingSpaces
        self.con = sqlite3.connect(pathProject + r'\system files\DataBase\carsBD.db')    # подключаем БД
        self.pathProject = pathProject

    # сохранение экзапилятора окна
    def getMainWindow(self, mainWindow) -> None:
        self.mainWindow = mainWindow

    # получение свободного места
    def getParkingSpaces(self) -> int:
        result = self.getAllNumberInBD()                  # получаем данные о номерах
        # получаем и смотрим свободные места
        allParkingSpaces = [i[4] for i in result]
        # перебераем все возможные места на парковке
        for spaces in range(1, self.countParkingSpaces + 1):
            if spaces not in allParkingSpaces:                 # возращяем свободное место
                return spaces
        return -1       # свободных мест нет

    # распазнование текста
    def capturing_number(self, plate: tuple, frame) -> str:
        # сохраняем коорд
        x, y, w, h = plate[0][0], plate[0][1], plate[0][2], plate[0][3]

        frame = frame[y:y + h, x:x + w]        # вырезаем нужное
        img_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)  # переводим в серое
        cv2.imwrite(self.pathProject + r"\resultsDetect\resultDect.png",
                    img_gray)  # сохраняем номер авто

        # конфиг для лучшего распазнования текста
        config = '--psm 6 --oem 3 -c tessedit_char_whitelist=ABEKMHOPCTYXakoyx0123456789'
        # читаем номер и возращяем результат
        return pytesseract.image_to_string(img_gray, config=config)

    # поиск номера в базе данных
    def searchNumdInBD(self, number: str) -> list:
        cur = self.con.cursor()
        result = cur.execute(f"""
        SELECT * FROM carsNumbers
        WHERE number = "{number}";""")
        result = [i for i in result]
        return result

    # удаление номера из базы данных
    def deletNumdInBD(self, number: str) -> None:
        cur = self.con.cursor()
        _ = cur.execute(f"""
        DELETE FROM carsNumbers
        WHERE number = '{number}';""")
        self.con.commit()

    # добавить номер в базу данных
    def addNumdInBD(self, allInf: tuple) -> None:
        cur = self.con.cursor()
        _ = cur.execute(f"""
        INSERT INTO carsNumbers
        VALUES ((SELECT Count(*) FROM carsNumbers), '{allInf[0]}', '{allInf[1]}', '{allInf[2]}', {allInf[3]}, {allInf[4]}, '{allInf[5]}');""")
        self.con.commit()

    # изменение инофрмации номера в базе данных
    def saveInforNumdInBD(self, allInf: tuple) -> None:
        cur = self.con.cursor()
        _ = cur.execute(f"""
        UPDATE carsNumbers
        SET number = '{allInf[0]}',
            FIO = '{allInf[1]}',
            dateStart = '{allInf[2]}',
            timeStopCar = {allInf[3]},
            numberParkingSpaice = {allInf[4]},
            blackList = {allInf[5]},
            otherInformation = '{allInf[6]}'
        WHERE number = '{allInf[0]}';""")
        self.con.commit()

    # получение всех номеров, которые находятся на парковке
    def getAllNumberInBD(self) -> list:
        cur = self.con.cursor()
        result = cur.execute(f"""
        SELECT * FROM carsNumbers;""")
        result = [i for i in result]
        return result

    # обработчик текста с результата распазнования
    def processingText(self, text: str) -> str:
        if len(text) < 8 or len(text) > 9:
            return ''

        # обрабатываем номер на наличие O и 0
        for index in range(len(text)):
            if index in [0, 4, 5] and text[index] == '0':
                text = text[:index] + 'O' + text[index + 1:]
            elif index == len(text) and text[index] == 'O':
                text = text[:index] + '0'
            elif index in [1, 2, 3, 6, 7, 8] and text[index] == 'O':
                text = text[:index] + '0' + text[index + 1:]

        return text.upper().strip()

    # распазнвоание номера машины на картинке
    def detectNumber(self, frame, quality=3) -> tuple:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        plate = self.number_plate_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=4,
            minSize=(50, 50))

        text = 'None'
        # нашел ли координаты (является ли plate - turple)
        if not isinstance(plate, tuple):
            resultText = self.processingText(self.capturing_number(
                plate, frame))     # получаем и обрабатываем текст

            if resultText and resultText != '\n':      # при адекватном прочтении
                # если пустой - добавляем номер
                # если последним был этот номер - добавляем
                # иначе удаляем все и начинаем заново

                if not self.replayNumber:
                    self.replayNumber.append(resultText)
                elif self.replayNumber[-1] == resultText:
                    self.replayNumber.append(resultText)
                else:
                    self.replayNumber = []
                    self.replayNumber.append(resultText)

            # если количество номеров соотвествует качеству выборки
            if len(self.replayNumber) == quality:
                res = self.replayNumber[-1]
                self.replayNumber = []
                return (True, res)

        return (False, text)

    # Открываем шлагбаум
    def openBarrier(self, infoNumber: list):
        infoNumber = infoNumber[0]
        cur = self.con.cursor()                  # получаем все номера на паровке
        result = cur.execute(f"""
        SELECT * FROM carsInParking
        WHERE number = "{infoNumber[1]}";""")
        result = [i for i in result]
        
        if not result:                 # добавляем тк машина заежает  
            _ = cur.execute(f"""
            INSERT INTO carsInParking
            VALUES ((SELECT Count(*) FROM carsInParking), '{infoNumber[1]}', '{infoNumber[2]}', '{datetime.datetime.now()}');""")
        else:                          # удаляем номер тк машина выезжает
            _ = cur.execute(f"""
            DELETE FROM carsInParking
            WHERE number = '{infoNumber[1]}';""")
        self.con.commit()
        
        # достаем всех машин на парковке
        result = cur.execute(f""" 
            SELECT * FROM carsInParking;""")

        self.mainWindow.openOrCloseBarrier(True)                      # вызываем открытие шлагбаума 
        self.mainWindow.displayNumberInParking(result)                # обновляем данные в таблице машин на парковке
    
    # автоматический обработчки номера
    def automaticDetect(self, infNum: list) -> bool:
        if not infNum:
            return False
        if infNum[0][5] == 1:
            return False
        return True
    
    # Номер определился
    def numberDefined(self, number: str) -> None:
        informNumber = self.searchNumdInBD(number)
        
        if self.mainWindow.automaticMode.isChecked():        # запущенна автоматическая проверка
            if self.automaticDetect(informNumber):
                self.openBarrier(informNumber)    
            return
        
        if self.mainWindow.displayDialogNumberInParking(informNumber, number):
            self.openBarrier(informNumber)
        return
