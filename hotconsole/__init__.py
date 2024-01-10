"""
Библиотека hotconsole - альтернатива argparse, которая позволяет совмещать консольные команды и горячие клавиши.
Облегчает процесс автоматизации рабочей рутины и подходит в т.ч. для тех, кто мало пишет на питоне.
Вам не нужно писать кучу инфраструктурного кода, просто напишите то, что хотите сделать.

**Запуск команд**

Рассмотрим простой пример пользовательского main.py - с командой для остановки службы

from hotconsole.commands import Command, Hotkey, Runner
from hotconsole.helpers import OSHelper

TurnService = Command("turn", "Отключить службу", labmda_: OSHelper.try_stop_service("SERVICE"))

def main():
    Runner().run([Hotkey("alt+t", TurnService, None)])

Что происходит при запуске main.py:
- Появится окошко со списком горячих клавиш
- При нажатии alt+t останавливается служба SERVICE
- Также можно нажать alt+q, перейти в консольный режим, написать turn - и получить тот же результат

А также: 
- Сгенерируется батник для установки библиотек (альтернативна pip install для ваших пользователей)
- У пользователя появится конфиг data.json в папке с main.py

**Опции**

Когда у нас парочка скриптов - можно создавать команды и без опций. Тогда по нажатию горячей клавиши сразу будет выполняться нужное действие. 

С этим подходом возникают проблемы, когда скриптов становится много - и при этом они тематически тесно связаны. В результате приходится создавать однотипные команды и запоминать / просматривать в списке десятки горячих клавиш. 

Решение - создавать определенные команды с опциями. У пользователя будет автоматически уточняться номер опции и передаваться в вашу функцию в качестве аргумента. 

Например, при создании команды передаем опции ["Включить", "Выключить", "Перезапустить"]   
Тогда функция будет выглядеть так:

def turn_service(option_number):
    match option_number:
            case 1:
                OSHelper.try_stop_service("SERVICE")
            case 2:
                OSHelper.try_start_service("SERVICE")
            case 3:
                OSHelper.try_rerun_service("SERVICE")

А команда так:
TurnService = Command("turn", "Изменить состояние службы", turn_service, ["Включить", "Выключить", "Перезапустить"])

- При нажатии alt+t в консоли появится список вариантов: 1. Выключить, 2, Включить, 3. Перезапустить
- При выборе варианта выполнится соответствующее действие
- В горячей клавише можно указать параметр, например, 1 - и тогда служба остановится без вопросов в консоли
- В консольном режиме можно написать turn 1 - и тогда служба остановится без вопросов в консоли

Также можно передать в команду option_message - вопрос, который будет уточнять у пользователя номер опции. По умолчанию это фраза "Введите номер варианта"

**Возможности конфигурации**

При первом запуске main.py - создается конфиг data.json с версией = 1. 

Конфиг полезен:
1) Для кэширования. Если в процессе выполнения команды нужно сохранить значение переменной, то можно в этот файл
2) Для кастомизации. Например, по умолчанию в конфиге есть поле console_mode. Пользователь может выставить его в True и перейти в консольный режим без горячих клавиш. 
3) Для обновления. Если версия конфига пользователя неактуальна (расходится с версией в файле main.py), в конфиг автоматически добавляются новые поля. Также можно вставить в процесс инициализации миграцию.

Создаем конфиг для передачи в Runner: config = Config (version=22, consoleMode=False, refuseStartup=False, isAnything = False)

Допустим, в 22 версии изменилось поле "isSomething" на "isAnything". Чтобы не потерять данные наших пользователей, можем сделать миграцию:

def migration_to_22():
    config = OSHelper.extract_whole_json(CONFIG_PATH)
    if "consoleModeIsDefault" in config.keys():
        config["isAnything"] = config["isSomething"]
        OSHelper.write_file(CONFIG_PATH, json.dumps(config, indent=4))

Также может возникнуть потребность перед запуском каждой команды выполнять определенные действия и актуализировать данные пользователя. Для этого при создании Runner в него можно передать метод для актуализации. 

**Hotstrings**

Hotstring - это как горячая клавиша, но только для строк. 
Например, мы можем создать Hotstring("githot", "Гитхаб hotconsole", "https://github.com/Vecheren/hotconsole")
И передать массив таких объектов в метод run.

Работает это так: пишем githot, нажимаем пробел - вместо githot в нашем случае подставляется ссылка.
"""

from hotconsole.commands import *
from hotconsole.helpers import *
import ansicon

OSHelper.rerun_as_admin()
OSHelper.set_english_layout()
ansicon.load()
