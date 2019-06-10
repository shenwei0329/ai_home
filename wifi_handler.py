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
import datetime
import snd_mail
import mongodb_class
import datetime

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
    _f = open("mac_rec.txt","r")
    while True:
        _s = _f.readline()
        if len(_s) == 0:
            break
        fix_mac.append(_s.replace("\n", ""))


def main():
    global oui_list

    db = mongodb_class.mongoDB()
    db.connect_db("wifi_probe")

    load_oui()
    load_fix_mac()
    # print oui_list


    # _sql = {"type":"00", "sub_type": "04", "$and": [{"tc": {"$gt": "2019-03-04 09:00:00"}}, {"tc":{"$lte": "2019-03-04 18:00:00"}}, {'RSSI': {"$lte": "-90"}}]}
    _sql = {"type":"00", "sub_type":"04", "$and": [{"tc": {"$gt": "2019-03-06 00:00:00"}}, {"tc":{"$lte": "2019-03-06 24:00:00"}}, {'RSSI': {"$lte": "-90"}}]}

    _rec = db.handler("rec", "find", _sql)

    print _rec.count()

    for _r in _rec:

        if _r['src'] in fix_mac:
            continue

        if _r['dst'] not in fix_mac:
            if _r['dst'] not in dst_list:
                dst_list[_r['dst']] = {'src': [], 'RSSI': []}
            dst_list[_r['dst']]['src'].append(_r['src'])
            dst_list[_r['dst']]['RSSI'].append(_r['RSSI'])

        if _r['src'] not in dev_list:
            dev_list[_r['src']] = []
        dev_list[_r['src']].append(_r['RSSI'])

    print("> %d, %d" % (len(dev_list), len(dst_list)))

    for _d in dev_list:
        if _d not in dst_list:
            mobile_list.append(_d)


    print('-'*32)


    _mobile_count = 0

    for _r in mobile_list:
        _count = len(dev_list[_r])
        _name = mac_format(_r)
        _min, _avg, _max = disp_rssi(dev_list[_r])

        _d_min = abs(_min - _avg)
        _d_max = abs(_max - _avg)
        _d = max([_d_min, _d_max])
        if _d >= 8:
            print "\t", _r, " : ", _name, " -- (", _count, ") [", _min, ", ", _avg, ", ", _max, "]"
            _mobile_count += 1
        # print("\t%s : %s -- (%d) [%d, %d, %d]" % (_r, _name, _count, _min, _avg, _max ))

    print(">>> %d / %d <<<" % (_mobile_count, len(dev_list)))


    _set_count = 0
    print('*'*32)

    for _r in dst_list:

        if len(dst_list[_r]['src']) < 5:
            continue

        _min, _avg, _max = disp_rssi(dst_list[_r]['RSSI'])
        if len(dst_list[_r]['src']) > 10:
            print("\t%s : %s -- (%d) [%d, %d, %d]" % (_r, mac_format(_r), len(dst_list[_r]['src']), _min, _avg, _max ))
            _set_count += 1

    print(">>> %d / %d <<<" % (_set_count, len(dst_list)))


if __name__ == "__main__":

    main()

#
#
