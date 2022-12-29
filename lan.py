try:
    import usocket as socket
except:
    import socket

import network, time, ntptime
import esp
from json import dump as jdump
from json import load as jload
from machine import Pin, unique_id

esp.osdebug(None)

import gc

hl_timezone = 7

def DoST(ssid, password):
    st = network.WLAN(network.STA_IF)
    st.active(True)
    while st.active() == False:
        pass
    try:
        st.connect(ssid, password)
    except:
        pass
    Start_sec = time.time()
    Now_sec = time.time()
    while (st.isconnected() == False) and (Now_sec - Start_sec) < 10:
        pass
        Now_sec = time.time()
    if st.isconnected():
        print('Station mode')
        print(st.ifconfig())
    return st.isconnected()


def DoAP(ssid, password):
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=ssid, password=password)
    ap.ifconfig(('192.168.25.1', '255.255.255.0', '192.168.25.1', '8.8.8.8'))
    while ap.active() == False:
        pass
    print('Access point mode')


def InitAP():
    try:
        _my_ssid, _my_password = wifi_cfg["my_ssid"], wifi_cfg["my_password"]
    except:
        print('Ошибка чтения параметров собственной точки доступа')
        ssid_sufix = "".join('{:02x}'.format(x) for x in unique_id())
        _my_ssid = "HL32_" + ssid_sufix
        _my_password = "123456789"
        DoAP(_my_ssid, _my_password)
        # ToDo Запускаем со своим паролем, если его нет то со стандартным потом ждём нажатия на флэш 5 сек для сброса пароля на 123456789
    else:
        print('AP access:', _my_ssid, _my_password)
        DoAP(_my_ssid, _my_password)
    finally:
        Start_sec = time.time()
        Now_sec = time.time()
        pinF = Pin(0, Pin.IN)
        while (pinF.value() == 1) and (Now_sec - Start_sec) < 5:
            Now_sec = time.time()
        if pinF.value() == 0:
            print("AP password reset")
            ssid_sufix = "".join('{:02x}'.format(x) for x in unique_id())
            _my_ssid = "HL32_" + ssid_sufix
            _my_password = "123456789"
            DoAP(_my_ssid, _my_password)


print("Connect to lan...")
gc.collect()
try:
    wifi_cfg_file = open("wifi.cfg", "r")
except:
    print('Error opening "wifi.cfg"')
    ssid_sufix = "".join('{:02x}'.format(x) for x in unique_id())
    wifi_cfg = {'my_ssid': "HL32_" + ssid_sufix, 'my_password': '123456789'}
    wifi_cfg_file = open("wifi.cfg", "w")
    jdump(wifi_cfg, wifi_cfg_file)
    wifi_cfg_file.close()
else:
    wifi_cfg = jload(wifi_cfg_file)
    try:
        _ssid, _password = wifi_cfg["ssid"], wifi_cfg["password"]
        DoST(_ssid, _password)
    except:
        print('Error reading AP parameters')
        InitAP()
    else:
        if not DoST(_ssid, _password):
            InitAP()
        else:
            print("Connected")
            try:
                ntptime.s
                ntptime.NTP_DELTA = ntptime.NTP_DELTA - hl_timezone * 3600
                ntptime.settime()
            except:
                print('Не удалось получить время')

# TODO Выход из конфигурации точки доступа по таймауту. Выяснить почему по сбросу выходит
# TODO Пароль на вход
