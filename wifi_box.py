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

import sys
import time
import datetime
import snd_mail
import mongodb_class
import datetime

import numpy as np
import matplotlib.pyplot as plt

device = {}

alarm_info = ""

send_st = 0


oui_list = {}
dev_list = {}
dst_list = {}
mobile_list = []

fix_mac = []

channel_mark = ['o', 'D', 'h', '-', 'p', '+', '.', 's', '*', 'd', 'v', '<', '>', '^','x']


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


def read_fix_mac(_f):
    while True:
        _s = _f.readline()
        if len(_s) == 0:
            break
        fix_mac.append(_s.replace("\n", ""))


def build_tc(tc_n, init_v):
    _x = np.arange(0,tc_n,1)
    _y = []
    for _i in _x:
        _y.append(init_v)
    return _x, _y


def get_tc_sec(tc):
    """2019-03-04 09:08:35.497213"""
    if ' ' in tc:
        _s = tc.split(' ')[1]
    else:
        return None
    _s = _s.split('.')[0]
    _s = _s.split(':')
    if len(_s) == 3:
        _tc = (int(_s[0])*60 + int(_s[1]))*60 + int(_s[2])
    else:
        return None
    return _tc


def get_tc_min(tc):
    """2019-03-04 09:08:35.497213"""
    if ' ' in tc:
        _s = tc.split(' ')[1]
    else:
        return None
    _s = _s.split('.')[0]
    _s = _s.split(':')
    if len(_s) == 3:
        _tc = (int(_s[0])*60 + int(_s[1])) / 5 
    else:
        return None
    return _tc


def main():
    global oui_list


    _f = open("mac_rec.txt","r")
    read_fix_mac(_f)
    _f.close()

    _f = open("mac_rec.txt","a")

    db = mongodb_class.mongoDB()
    db.connect_db("wifi_probe")

    load_oui()
    # print oui_list


    """
    _sql = {"type":"02",
            "$and": [{"tc": {"$gt": "2019-03-04 23:00:00"}},
                {"tc":{"$lte": "2019-03-05 02:00:00"}},
                {'RSSI': {"$lte": "-90"}}]
            }
    """
    _sql = {
            # "type": "02",
            # "type": sys.argv[1],
            # "sub_type": sys.argv[2],
            # "src": sys.argv[3],
            # "src": "7C:11:CB:8A:C8:58",
            # "src": "A0:3B:E3:C7:2A:88",
            # "src": "10:44:00:35:B6:E4",
            "$and": [{"tc": {"$gt": "2019-03-06 00:00:00"}},
                {"tc":{"$lte": "2019-03-06 23:59:59"}},
                # {'RSSI': {"$lte": "-80"}}
                ]
            }

    if sys.argv[1] != '-':
        _sql['type'] = sys.argv[1]
    if sys.argv[2] != '-':
        _sql['sub_type'] = sys.argv[2]
    if sys.argv[3] != '-':
        _sql['src'] = sys.argv[3]

    _rec = db.handler("rec", "find", _sql)

    print _rec.count()

    _x, _y = build_tc(12*24,[])


    _t = {}

    for _r in _rec:
        _tc = get_tc_min(_r['tc'])
        if _tc is not None:
            # print _tc
            if _tc not in _t:
                _t[_tc] = []
            _t[_tc].append(int(_r['RSSI']))
        # print _t[_tc]

    for _r in _t:
        _y[_r] = _t[_r]

    # print _y
    plt.boxplot(_y, showfliers=False)
    plt.show()


if __name__ == "__main__":

    main()

#
#
