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

from __future__ import print_function

import time
import datetime
import snd_mail
import mongodb_class
import datetime
import cal_rssi

device = {}

alarm_info = ""

send_st = 0


oui_list = {}
dev_list = {}
dst_list = {}
mobile_list = []
fix_mac = []


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


def disp_rssi(rssi):

    _v = []

    _sum = 0

    for _r in rssi:
        _v.append(int(_r))
        _sum += int(_r)

    return min(_v), _sum/len(rssi), max(_v)


def load_fix_mac():
    _f = open("mac_rec.txt", "r")
    while True:
        _s = _f.readline()
        if len(_s) == 0:
            break
        fix_mac.append(_s.replace("\n", ""))


def timestamp(ti):
    return int(time.mktime(ti.timetuple()))


def scale_ti(ti):
    return ti + datetime.timedelta(minutes=1)


def scale_ti_by_second(ti):
    return ti + datetime.timedelta(seconds=1)


def main():
    global oui_list

    # load_oui()
    # load_fix_mac()

    db = mongodb_class.mongoDB()
    db.connect_db("wifi_probe")

    _bg_time = (datetime.date.today() + datetime.timedelta(days=-0)).strftime("%Y-%m-%d") + " 00:00:00"
    _now = str(datetime.datetime.now()).split(' ')[0] + " 24:00:00"
    _sql = {
            "src": "10:44:00:35:B6:E4",
            # "type": "02",
            "$and": [{"tc": {"$gt": _bg_time}},
                     {"tc": {"$lte": _now}},
                     ]
            }
    _rec = db.handler("rec", "find", _sql)

    print("\n%s:<%d>\n" % (_sql, _rec.count()))
    if _rec.count() == 0:
        return

    _rssi = {}
    _cnt = 80
    for _r in _rec:
        if 'ip' in _r:
            continue
        # _tc = datetime.datetime.strptime(_r['tc'].split('.')[0], "%Y-%m-%d %H:%M:%S")
        _tc = datetime.datetime.strptime(_r['tc'].split('.')[0][:16], "%Y-%m-%d %H:%M")
        _ts = timestamp(_tc)
        _rssi[_ts] = cal_rssi.cal_distance_by_rssi(int(_r['RSSI']))

    _now = datetime.datetime.now()
    _now += datetime.timedelta(seconds=-_now.second,
                               minutes=30-_now.minute,
                               hours=8-_now.hour,
                               microseconds=-_now.microsecond,
                               days=-0)

    _now_day = _now.day
    _bg_date = _now
    _s = '+'
    _cnt = 1
    _ss = ""
    while _now.day == _now_day:
        _now = scale_ti(_now)
        _ts = timestamp(_now)

        print(" " * _cnt, end="\r")
        _s = "%s " % _now
        _cnt = len(_s)
        print(_s, end="")

        if _ts in _rssi:
            _ss = '-' * abs(int(_rssi[_ts]*3)) + "*"+"[%d]" % _rssi[_ts]

        _cnt += len(_ss)
        print(_ss, end="\r")
        time.sleep(0.1)


if __name__ == "__main__":

    main()

#
#
