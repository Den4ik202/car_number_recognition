Проект - распознавание машинных номеров с графической оболочкой при помощи PyQt6

Основные функции проекта:
— Можно открывать/закрывать виртуальный шлагбаум
— Текстовый редактор с возможность сохранить и удалить весь текст
— Режим автоматической проверки - при распознавании автомобильного номера программа будет сама решать, пускать автомобиль или нет
— Если номер распознался, а автом. режим не включен, то пользователю дается выбор, пускать или нет автомобиль (если номера нет в списке или он находиться в черном списке программа предупредит об этом)
— Видео поток, где отображается фреймы с камеры
— Таблица с машинами, которые находятся на автостоянке
— Возможность открыть поиск номеров из базы данных
— Возможность найти/сохранить/изменить/удалить номер в базе данных. При возникших ошибках программа предупредит
— Просмотр всех номеров в базе данных

В папке "code" храниться код программ:
— main.py - главный файл, от которого идет запуск всей программы
— mainClass.py - главный класс, где храниться функционал, связанный с работой с таблицей, распознаванием авто-номера и тд.
— allWidget.py = программа с подключением и описанием функционала всех используемых виджетов

В папке "resultDetect" храниться фото, которое программа сфокусировала при считывании текста с номера

В папке "system files" хранятся системные файлы, такие как:
— Модуль для распознавания текста с картинки
— Модуль для захвата номера с картинки

В папке "visualization" хранятся:
— ui-файлы с описанием всех виджетов графически
— Изображения, которые используются во время исполнения программы


exe файл для запуска программы лежит в каталоге "\code\dist\main\main.exe"

haarcascade_russian_plate_number.xml нужен для поиска номера на изображении
Взял у - https://github.com/spmallick/mallick_cascades/blob/master/haarcascades/haarcascade_russian_plate_number.xml
