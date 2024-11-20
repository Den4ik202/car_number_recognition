import os
import sys
import datetime        # для работы с датой и временем
import cv2             # машиное зрение

# импорт библиотеки для работы с визуализацией
from PyQt6.QtWidgets import QApplication

# импорт всех модулей
from mainClass import SmartGuard
from allWidget import MainWindow

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)  # Создание экземпляра VideoCapture

    # подключаем класс для распазнования маш. номеров
    pathProj = str(os.path.abspath(os.getcwd())).split('Reconing Car Number')[0] + 'Reconing Car Number' # путь до всех системных файлов
    smartGuard = SmartGuard(pathProj + r'\system files\RecText\Tesseract-OCR\tesseract.exe', pathProj)
    app = QApplication(sys.argv)
    ex = MainWindow(smartGuard, pathProj)
    smartGuard.getMainWindow(ex)
    ex.show()
      
    chekBarrier = False                            # флаг для проверки, открыт ли шлагбаум 
    timeExpectationToOpenBarrier = 15              # время, через которое закроется шлагбаум, в секундах
    timeOpenBarrier = datetime.datetime.now()      # время, в которое был открыт шлагбаум
    timeNow = datetime.datetime.now()              # текущее время
    
    while True:                   # Запуск видеопотока
        _, frame = cap.read()     # Чтение кадра и получение его свойств
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)     # преобразование цветовой палитры
        ex.updateImage(frame)     # обнавляем картинку

        resultDetect, textDetect = smartGuard.detectNumber(frame, 3)
        timeNow = datetime.datetime.now()
        
        if resultDetect and not ex.getStateBarrier():           # если мы получили результат, но шлагбаум закрыт
            smartGuard.numberDefined(textDetect)

        # ------------------------ обработчик шлагбаума ---------------------------------
        if ex.getStateBarrier() and not chekBarrier:   # если шлагбаум открыт и мы это пропустили
            chekBarrier = True
            timeOpenBarrier = datetime.datetime.now()  # запускаем таймер 
            continue
        
        if not ex.getStateBarrier() and chekBarrier:   # останавливаем слежку, если шлагбаум закрылся
            chekBarrier = False
        
        if int(float(str(timeNow - timeOpenBarrier).split(':')[2])) > timeExpectationToOpenBarrier and chekBarrier:
            ex.openOrCloseBarrier(False)        # закрываем, если прошлои времени больше n-секунд и мы заметили это
            chekBarrier = False
            
            
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Остановка видеопотока
            break

    cap.release()                      # Закрытие видеопотока
    cv2.destroyAllWindows()
    sys.exit(app.exec())