# -*- coding: UTF-8 -*-
#
# AI@Home
# =======
# Version: 0.8
#
# 2019.3.2 @Home
# ---------------
#
#
#

import time
import serial
import datetime
import snd_mail
import mongodb_class
import datetime

device = {}

alarm_info = ""

send_st = 0


oui_list = {}
dev_list = {}


def load_oui():
    f = open('oui.txt')
    while True:
        _l = f.readline()
        if len(_l) > 0:
            if "(hex)" in _l:
                _t = _l.replace('(hex)','').replace('\t','').replace('\n','').replace('\r','').split('  ')
                oui_list[_t[0]] = _t[1]
        else:
            break


def mac_format(mac):
    _m = mac.replace(':', '-')
    if _m[0:8] in oui_list:
        return oui_list[_m[0:8]]


def Hex2Int(h):
    _v = "0123456789ABCDEF"
    _h = _v.index(h[0])
    _l = _v.index(h[1])
    return _h*16+_l


def main():
    global oui_list

    try:
        db = mongodb_class.mongoDB()
        db.connect_db("wifi_probe")

        load_oui()
        # print oui_list

        # ser = serial.Serial('/dev/tty.usbserial-1420', 115200)
        ser = serial.Serial('com3', 115200)
        # ser = serial.Serial('/dev/ttyUSB0', 115200)
    except:
        return

    _str = ""

    while 1:

        while ser.inWaiting() > 0:

            _c = ser.read(1)
            if _c not in "\n\r":
                _str += _c
            else:
                _mac = _str.split('|')

                if len(_mac)>=6 and _mac[5].replace('-', '').isdigit() and abs(int(_mac[5]))<=90:

                    _now = str(datetime.datetime.now())
                    _rec = {'tc': _now, 'src': _mac[0], 'dst': _mac[1], 'type': _mac[2], 'sub_type': _mac[3], 'channel': _mac[4], 'RSSI': _mac[5]}
                    try:
                        db.handler("rec", "insert", _rec)
                    except:
                        return

                    if _mac[0] not in dev_list:
                        # print("\t%s <%s.%s.%s>:\t%s [%s] <-> %s [%s]" % (_mac[5],_mac[2],_mac[3],_mac[4],mac_format(_mac[0]),_mac[0][9:],mac_format(_mac[1]),_mac[1][9:]))
                        _rec["status"] = 0 
                        _rec["lifetime"] = 300
                        _rec["out_count"] = 0
                        _rec["in_count"] = 0
                        dev_list[_mac[0]] = _rec
                    else:
                        if _mac[5] != dev_list[_mac[0]]['RSSI']:
                            # print("\t%s <%s.%s.%s>:\t%s [%s] <-> %s [%s]" % (_mac[5],_mac[2],_mac[3],_mac[4],mac_format(_mac[0]),_mac[0][9:],mac_format(_mac[1]),_mac[1][9:]))
                            dev_list[_mac[0]]['RSSI'] = _mac[5]

                        dev_list[_mac[0]]['lifetime'] = 300
                _str = ""

        time.sleep(1)

        _in_sum = 0
        _out_sum = 0
        _warn_sum = 0

        updated = False

        for _d in dev_list:

            if 'lifetime' not in dev_list[_d]:
                continue

            if dev_list[_d]['lifetime']>0:
                if dev_list[_d]['status'] ==0:
                    if "10:44:00:35:B6:E4" in str(_d):
                        print("========>"),
                    print("> %s\t%s < IN!\tcount[ %d ]" % (
                        _d,
                        dev_list[_d]['RSSI'],
                        dev_list[_d]['in_count']))
                    dev_list[_d]['status'] = 1
                    dev_list[_d]['in_count'] += 1
                    updated = True
                dev_list[_d]['lifetime'] -= 1
            else:
                if dev_list[_d]['status'] == 1:
                    dev_list[_d]['status'] = 2
                    dev_list[_d]['lifetime'] = 30 
                elif dev_list[_d]['status'] == 2:
                    dev_list[_d]['status'] = 0
                    if "10:44:00:35:B6:E4" in str(_d):
                        print("========>"),
                    print("> %s < OUT!" % _d)
                    updated = True
                    dev_list[_d]['out_count'] += 1

            if dev_list[_d]['status'] == 1:
                _in_sum += 1
            elif dev_list[_d]['status'] == 2:
                _warn_sum += 1
            else:
                _out_sum += 1

        if updated:
            print("< %d, %d, %d >" % (_in_sum, _warn_sum, _out_sum))


if __name__ == "__main__":

    while True:
        main()
        time.sleep(60)

#
#
