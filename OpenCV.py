import cv2
from pytesseract import pytesseract

def capturing_number(plate: tuple) -> str:     # захват автомобильного номера
    x, y, w, h = plate[0][0], plate[0][1], plate[0][2], plate[0][3]               # сохраняем

    for (x, y, w, h) in plate:  # пробегаемся по координатам
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)            # рисуем прямоугольник (не обязательно)

    (_, dark_im) = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY) # переводим в черно-белое
    cv2.imwrite("res.png", dark_im[y:y + h, x:x + w])                    # сохраняем только номер авто

    return pytesseract.image_to_string('res.png', lang='eng', config='--psm 8')              # читаем номер

def delete_trash(text_im_img: str) -> str:   # удаление "мусора" и превращение в красивый вид
    if len(text_im_img) < 8:   # возращаем False, если длинна меньше наименьшей
        return ''
    result_text = ''

    for i in range(len(text_im_img) - 1):
        if text_im_img[i].isalnum():
            result_text += text_im_img[i].upper()

    if len(result_text) < 8:   # возращаем False, если длинна меньше наименьшей
       return ''
    result_text = result_text.replace('O', '0')
    return result_text




cap = cv2.VideoCapture(0)  # Создание экземпляра VideoCapture
number_plate_cascade = cv2.CascadeClassifier('haarcascade_russian_plate_number.xml')  # подключение каскада
pytesseract.tesseract_cmd = r'C:\Users\User\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'


while True:                                # Запуск видеопотокайй
    ret, frame = cap.read()                # Чтение кадра и получение его свойств
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    plate = number_plate_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=4,
        minSize=(50, 50))

    replay_number = []       # для сохранения пред. номера

    if not isinstance(plate, tuple):       # нашел ли координаты (является ли plate - turple)
        res_text = delete_trash(capturing_number(plate))
        print(res_text)

        if res_text and res_text != '\n':
            if not replay_number:
                replay_number.append(res_text)
            elif replay_number[-1] == res_text:
                replay_number.append(res_text)
            else:
                replay_number = []
                replay_number.append(res_text)

        #print(replay_number)
        if len(replay_number) == 3:
            print(replay_number[0], '------------------------')

        # x, y, w, h = plate[0][0], plate[0][1], plate[0][2], plate[0][3]                # сохраняем
        # for (x, y, w, h) in plate:                                                     # пробегаемся по координатам
        #     cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)             # и рисуем прямоугольник (не обязательно)
        # (_, dark_im) = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY)  # переводим в черно-белое
        # cv2.imwrite("res.png", dark_im[y:y + h, x:x + w])                     # сохраняем только номер авто
        # text_image = pytesseract.image_to_string('res.png', lang='eng')
        # result_text = ''
        #
        # for i in range(len(text_image) - 1):
        #     if text_image[i].isalnum():
        #         result_text += text_image[i]
        #
        # print(result_text)
        #
        # if len(result_text) == 8:
        #     print(result_text)

        #
        # print(x, y, w, h)
        # cv2.imwrite("res.jpg", frame[y:y + h, x:x + w])

    cv2.imshow("Video", frame)           # Отображение кадра
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Остановка видеопотока
        break

cap.release()                      # Закрытие видеопотока
cv2.destroyAllWindows()            # Закрытие всех окон
