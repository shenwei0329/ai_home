# main.py

import network
import webrepl
import utime
import socket
import machine

SSID = "CETC-CD-6"
PASSWORD = "cetccd123"

# SSID = "Tenda_3F5B88"
# PASSWORD = "13880575001"

def do_connect():

    import network

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.scan()

    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(SSID, PASSWORD)

    start = utime.time()

    while not wlan.isconnected():
        utime.sleep(1)
        if utime.time()-start > 30:
            print("connect timeout!")
            break

    if wlan.isconnected():
        print('network config:', wlan.ifconfig())

do_connect()

webrepl.start()

uart = machine.UART(0)

ss = None
_conn = False

while True:

    if not _conn:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # s.connect(('192.168.0.103', 64420))
            s.connect(('10.111.135.4', 64420))
        except:
            print(">>> connect err! <<<")
            utime.sleep(1)
            continue
        _conn = True

    _s = uart.readline()
    if _s is None:
        utime.sleep_ms(500)
    else:
        if "\n" in _s:
            if ss is None:
                ss = _s
            else:
                ss += _s
            print("%s" % ss)
            try:
                s.sendall(ss)
            except:
                s.close()
                _conn = False
                continue
            ss = None
        else:
            if ss is None:
                ss = _s
            ss += _s

