import serial
import time

bv = serial.Serial('COM4', 19200)

command_poll = b'\x02\x03\x06\x33\xDA\x81'
command_reset = b'\x02\x03\x06\x30\x41\xb3'
command_enable = b'\x02\x03\x0C\x34\xFF\xFF\xFF\x00\x00\x00\xB5\xC1'
command_disable = b'\x02\x03\x0C\x34\x00\x00\x00\x00\x00\x00\xB5\xC1'
ack = b'\x02\x03\x06\x00\xC2\x82'

status_initializing = b'\x02\x03\x06\x13\xd8\xa0'
status_disabled = b'\x02\x03\x06\x19\x82\x0f'
status_idling = b'\x02\x03\x06\x14\x67\xd4'
status_accepting = b'\x02\x03\x06\x15\xee\xc5'
status_stacking = b'\x02\x03\x06\x17\xfc\xe6'
status_jamstacker = b'\x02\x03\x06\x44\xe2\x86'
status_nostacker = b'\x02\x03\x06\x42\xd4\xe3'
status_accepted = b'\x02\x03\x07\x81'


def cashcode_reset():
    bv.write(command_reset)
    time.sleep(0.02)
    if bv.read(bv.in_waiting) == ack:
        print('Получен ожидаемый ответ: АСК. Значит, кэшкод уже перезагружается.')
    else:
        print('Вместо ожидаемого АСК мы получили... ', bv.read(bv.in_waiting))
        bv.write(ack)
        if bv.in_waiting > 0:
            bv.read(bv.in_waiting) #очищаем буфер

def cashcode_enable():
    bv.write(command_enable)
    time.sleep(0.02)
    if bv.read(bv.in_waiting) == ack:
        print('Получен ожидаемый ответ: АСК. Значит, кэшкод разрешил все купюры для приёма.')
    else:
        print('Вместо ожидаемого АСК мы получили... ', bv.read(bv.in_waiting))
        bv.write(ack)
        if bv.in_waiting > 0:
            bv.read(bv.in_waiting) #очищаем буфер

def cashcode_disable():
    bv.write(command_disable)
    time.sleep(0.02)
    if bv.read(bv.in_waiting) == ack:
        print('Получен ожидаемый ответ: АСК. Значит, кэшкод запретил все купюры для приёма.')
    else:
        print('Вместо ожидаемого АСК мы получили... ', bv.read(bv.in_waiting))
        bv.write(ack)
        if bv.in_waiting > 0:
            bv.read(bv.in_waiting) #очищаем буфер

def cashcode_poll():
    bv.write(command_poll)
    time.sleep(0.02)
    if bv.read(2) == b'\x02\x03': #значит пришло что-то именно от кэшкода (а не какая-либо помеха)
        bv.read(1) #считываем длину пакета "в никуда"
        status = bv.read(1)
        if status == b'\x13': #статус INITIALIZING
            bv.write(ack)
            print('Получен ответ: ИНИЦИАЛИЗАЦИЯ.')
            bv.read(bv.in_waiting) #очищаем буфер
        elif status == b'\x19':
            bv.write(ack)
            print('Получен ответ: ОТКЛЮЧЕНО.')
            bv.read(bv.in_waiting) #очищаем буфер
        elif status == b'\x14':
            bv.write(ack)
            print('Получен ответ: ГОТОВ.')
            bv.read(bv.in_waiting) #очищаем буфер
        elif status == b'\x15':
            bv.write(ack)
            print('Получен ответ: ПРИЁМ КУПЮРЫ')
            bv.read(bv.in_waiting) #очищаем буфер
        elif status == b'\x17':
            bv.write(ack)
            print('Получен ответ: УКЛАДКА КУПЮРЫ В СТЕКЕР')
            bv.read(bv.in_waiting) #очищаем буфер
        elif status == b'\x44': #JAM IN STACKER
            bv.write(ack)
            print('Получен ответ: ЗАМЯТИЕ/ЗАСТРЕВАНИЕ КУПЮРЫ В СТЕКЕРЕ')
            bv.read(bv.in_waiting) #очищаем буфер
        elif status == b'\x43': #JAM IN ACCEPTOR
            bv.write(ack)
            print('Получен ответ: ЗАМЯТИЕ/ЗАСТРЕВАНИЕ КУПЮРЫ В КУПЮРОПРИЁМНИКЕ')
            bv.read(bv.in_waiting) #очищаем буфер
        elif status == b'\x42':
            bv.write(ack)
            print('Получен ответ: СНЯТ СТЕКЕР')
            bv.read(bv.in_waiting) #очищаем буфер
        elif status == b'\x47':
            error = bv.read(1)
            if error == b'\x55': #предположительно, возникает при откидывании крышки с датчиками
                bv.read(2) #считываем в никуда контрольную сумму (НУ А НАХУЙ ОНА ВООБЩЕ НУЖНА?)))))
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('FAILURE 55')
            else:
                bv.read(2)
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('FAILURE с иным кодом (что оно значит - без понятия): ', error)
        elif status == b'\x1c':
            print('НЕ УДАЛОСЬ РАСПОЗНАТЬ КУПЮРУ')
            error = bv.read(1) #считываем ещё один байт, содержащий в себе подробности ошибки
            if error == b'\x69':
                bv.read(2) #считываем в никуда контрольную сумму
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('CAPACITY ERROR')
            elif error == b'\x66':
                bv.read(2) #считываем в никуда контрольную сумму
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('VERIFICATION ERROR')
            elif error == b'\x64':
                bv.read(2) #считываем в никуда контрольную сумму
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('CONVEYING ERROR')
            elif error == b'\x6A':
                bv.read(2) #считываем в никуда контрольную сумму
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('OPERATION ERROR')
            else:
                bv.read(2)
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('ПОЛУЧЕН КОД ОШИБКИ, ЗНАЧЕНИЕ КОТОРОГО ПОКА НЕ ИЗУЧЕНО: ', error)
        elif status == b'\x81':
            nominal = bv.read(1) #считываем следующий байт, содержащий номинал купюры
            if nominal == b'\x02':
                bv.read(2) #считываем в никуда контрольную сумму
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('ПРИНЯТО 10 РУБЛЕЙ')
            elif nominal == b'\x03':
                bv.read(2) #считываем в никуда контрольную сумму 
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('ПРИНЯТО 50 РУБЛЕЙ') 
            elif nominal == b'\x04':
                bv.read(2) #считываем в никуда контрольную сумму 
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('ПРИНЯТО 100 РУБЛЕЙ')
            elif nominal == b'\x05':
                bv.read(2) #считываем в никуда контрольную сумму
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('ПРИНЯТО 500 РУБЛЕЙ')
            elif nominal == b'\x06':
                bv.read(2) #считываем в никуда контрольную сумму
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('ПРИНЯТО 1000 РУБЛЕЙ')
            elif nominal == b'\x07':
                bv.read(2) #считываем в никуда контрольную сумму
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('ПРИНЯТО 5000 РУБЛЕЙ')
            else:
                bv.read(2)
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('ПРИНЯТА НЕИЗВЕСТНАЯ НАУКЕ ИННОВАЦИОННАЯ БАНКНОТА: ', nominal)
    else: #если сообщение пришло от другой периферии, или это вообще мусор какой-то...
        print('Мы не знаем, что это такое. Если бы мы знали, что это такое. Мы не знаем, что это такое...', bv.read(bv.in_waiting))

print('Зрасссссссь!')
while bv.in_waiting > 0:
    bv.read()
print('Перезагружаем кэшкод...')
cashcode_reset()
time.sleep(5)
cashcode_poll()
time.sleep(0.5)
cashcode_poll()
time.sleep(0.3)
cashcode_enable()
time.sleep(0.2)
while bv.is_open:
    cashcode_poll()
    time.sleep(0.4)
