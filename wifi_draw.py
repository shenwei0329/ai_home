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
from datetime import datetime, date, timedelta

import snd_mail
import mongodb_class
import datetime

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from numpy import *

reload(sys)
sys.setdefaultencoding('utf8')

device = {}

alarm_info = ""

send_st = 0


oui_list = {}
mac_list = []
rec_list = {}


MAX_RSSI = 100 


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



# 计算欧几里得距离
def distEclud(vecA, vecB):
    return sqrt(sum(power(vecA - vecB, 2))) # 求两个向量之间的距离


# 构建聚簇中心，取k个(此例中为4)随机质心
def randCent(dataSet, k):

    # print shape(dataSet)

    n = shape(dataSet)[1]
    centroids = mat(zeros((k,n)))   # 每个质心有n个坐标值，总共要k个质心

    # print n
    # print centroids

    for j in range(n):

        minJ = min(dataSet[:,j])
        maxJ = max(dataSet[:,j])
        rangeJ = float(maxJ - minJ)
        centroids[:,j] = minJ + rangeJ * random.rand(k, 1)
    return centroids


# k-means 聚类算法
def kMeans(dataSet, k, distMeans =distEclud, createCent = randCent):
    m = shape(dataSet)[0]
    clusterAssment = mat(zeros((m,2)))    # 用于存放该样本属于哪类及质心距离
    # clusterAssment第一列存放该数据所属的中心点，第二列是该数据到中心点的距离
    centroids = createCent(dataSet, k)
    clusterChanged = True   # 用来判断聚类是否已经收敛
    while clusterChanged:
        clusterChanged = False;
        for i in range(m):  # 把每一个数据点划分到离它最近的中心点
            minDist = inf; minIndex = -1;
            for j in range(k):
                distJI = distMeans(centroids[j,:], dataSet[i,:])
                if distJI < minDist:
                    minDist = distJI; minIndex = j  # 如果第i个数据点到第j个中心点更近，则将i归属为j
            if clusterAssment[i,0] != minIndex: clusterChanged = True;  # 如果分配发生变化，则需要继续迭代
            clusterAssment[i,:] = minIndex,minDist**2   # 并将第i个数据点的分配情况存入字典
        # print centroids
        for cent in range(k):   # 重新计算中心点
            ptsInClust = dataSet[nonzero(clusterAssment[:,0].A == cent)[0]]   # 去第一列等于cent的所有列
            centroids[cent,:] = mean(ptsInClust, axis = 0)  # 算出这些数据的中心点
    return centroids, clusterAssment


def main():
    global oui_list


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

    yesterday = date.today() + timedelta(days = -1)
    _bg_time = yesterday.strftime("%Y-%m-%d") + " 00:00:00"
    _now = str(datetime.datetime.now()).split(' ')[0] + " 00:00:00"

    # _bg_time = "2019-03-07 00:00:00"
    # _now = "2019-03-07 23:59:59"

    """

    _bg_time = sys.argv[2] + " 00:00:00"
    _now = sys.argv[3] + " 00:00:00"

    print _bg_time, " --> ", _now

    _sql = {
            # "type": "02",
            # "type": sys.argv[1],
            # "sub_type": sys.argv[2],
            # "src": sys.argv[3],
            # "src": "7C:11:CB:8A:C8:58",
            # "src": "A0:3B:E3:C7:2A:88",
            # "src": "10:44:00:35:B6:E4",
            "$and": [{"tc": {"$gt": _bg_time}},
                {"tc":{"$lte": _now}},
                # {'RSSI': {"$lte": "-80"}}
                ]
            }

    if len(sys.argv) > 3:
        if sys.argv[1] != '-':
            _sql['type'] = sys.argv[1]
        """
        if sys.argv[2] != '-':
            _sql['sub_type'] = sys.argv[2]
        if sys.argv[3] != '-':
            _sql['src'] = sys.argv[3]
        """

    print _sql

    _rec = db.handler("rec", "find", _sql)

    print _rec.count()

    _fix_mac = [
            "A4:56:02:F0:CA:9A",
            "70:F9:6D:16:CF:69"
            ]
    for _r in _rec:

        if _r['src'] in _fix_mac:
            continue

        if _r['src'] not in mac_list:
            mac_list.append(_r['src'])

        if _r['src'] not in rec_list:
            rec_list[_r['src']] = []
        rec_list[_r['src']].append(_r)

    _x, _y = build_tc(12*24, -110)
    _y_min = []
    for _v in _y:
        _y_min.append(0)

    for _mac in mac_list:

        # print(">>> mac: %s" % _mac)

        """
        _sql['src'] = _mac
        _rec = db.handler("rec", "find", _sql)
        print _rec.count()
        """
        _rec = rec_list[_mac]
        # print len(_rec)

        _yy = []
        _yy_ip = []

        # ax1 = plt.subplot(2,1,1)
        ax2 = plt.subplot(1,1,1)

        """
        ax1.set_xlim([-12, 300])
        ax1_d = ax1.twiny()
        ax1_d.set_xlim(-1,25)
        # 9:00
        # 11:30
        # 12:00
        # 13:30
        # 17:30
        ax1.plot([108,108],[-100,0],'r--', linewidth=0.5)
        ax1.plot([138,138],[-100,0],'g--', linewidth=0.5)
        ax1.plot([144,144],[-100,0],'g--', linewidth=0.5)
        ax1.plot([162,162],[-100,0],'g--', linewidth=0.5)
        ax1.plot([210,210],[-100,0],'r--', linewidth=0.5)
        """

        ax2.set_xlim([-12, 300])
        ax2.plot([108,108],[-100,0],'r--', linewidth=0.5)
        ax2.plot([138,138],[-100,0],'g--', linewidth=0.5)
        ax2.plot([144,144],[-100,0],'g--', linewidth=0.5)
        ax2.plot([162,162],[-100,0],'g--', linewidth=0.5)
        ax2.plot([210,210],[-100,0],'r--', linewidth=0.5)
        # ax2_d = ax2.twiny()
        # ax2_d.set_xlim(0,24)

        for _r in _rec:

            # print _r['tc']
            _tc = get_tc_min(_r['tc'])
            if _tc is not None:
                
                try:
                    _v = int(_r['RSSI'].split(' ')[0])
                except:
                    continue

                _y[_tc] = max(_y[_tc], _v)
                _y_min[_tc] = min(_y_min[_tc], _v)
                if 'ip' in _r:
                    _yy_ip.append(map(float, [_tc, MAX_RSSI + _v]))
                else:
                    _yy.append(map(float, [_tc, MAX_RSSI + _v]))

                _err = False
                try:
                    if 'ip' in _r:
                        plt.sca(ax1)
                    else:
                        plt.sca(ax2)
                    plt.plot(_tc, int(_r['RSSI']), 'b+')
                except Exception, e:
                    print e
                    _err = True
                finally:
                    if _err:
                        print(">>> %s: Error! <<<" % _r)
        
        if len(_yy) < 24:
            continue

        """
        # 用测试数据及测试kmeans算法
        _yy_ip = mat(_yy_ip)
        myCentroids,clustAssing = kMeans(_yy_ip, 24)
        print myCentroids
        # print clustAssing

        for _d in myCentroids:
            # print _d[:,0]
            _err = False
            try:
                __x = int(_d[:, 0])
                __y = int(_d[:, 1]) - MAX_RSSI
            except Exception, e:
                print e
                _err = True
            finally:
                if not _err:
                    plt.sca(ax1)
                    plt.plot(__x, __y, 'r^')
        """

        # 用测试数据及测试kmeans算法
        _yy = mat(_yy)
        myCentroids,clustAssing = kMeans(_yy, 24)
        print myCentroids
        # print clustAssing

        for _d in myCentroids:
            # print _d[:,0]
            _err = False
            try:
                __x = int(_d[:, 0])
                __y = int(_d[:, 1]) - MAX_RSSI
            except Exception, e:
                print e
                _err = True
            finally:
                if not _err:
                    plt.sca(ax2)
                    plt.plot(__x, __y, 'r^')

        # plt.plot(_x, _y, 'r+', _x, _y_min, 'g.')
        # plt.show()

        print "savefig: %s" % _mac
        plt.savefig("%s.png" % _mac, dpi=120)
        plt.clf()


if __name__ == "__main__":

    main()

#
#
