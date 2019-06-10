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

reload(sys)
sys.setdefaultencoding('utf-8')

import time
import serial
import datetime
import snd_mail
import mongodb_class
import datetime

import socketserver

device = {}

alarm_info = ""

send_st = 0


class echorequestserver(socketserver.BaseRequestHandler):

    def handle(self):

        self.oui_list = {}
        self.dev_list = {}
        self.db = mongodb_class.mongoDB()
        self.db.connect_db("wifi_probe")
        self.load_oui()

        print("starting...") 
        self.conn = self.request
        print('connected with: ', self.client_address)

        while True:
            self.client_data = self.conn.recv(1024)
            if not self.client_data:
                print('disconnect')
                break

            self.data_handler(self.client_address)

    def data_handler(self, ip):

        _pkt = bytes.decode(self.client_data).replace('\r', '').split('\n')

        for _p in _pkt:
            
            _mac = _p.split('|')

            if len(_mac) >= 6:

                _now = str(datetime.datetime.now())
                _rec = {'tc': _now, 'src': _mac[0], 'dst': _mac[1], 'type': _mac[2], 'sub_type': _mac[3], 'channel': _mac[4], 'RSSI': _mac[5]}
                _rec['ip'] = ip
                self.db.handler("rec", "insert", _rec)

                if _mac[0] not in self.dev_list:
                    print("\t%s <%s.%s.%s>:\t%s [%s] <-> %s [%s]" % (_mac[5],_mac[2],_mac[3],_mac[4],self.mac_format(_mac[0]),_mac[0][9:],self.mac_format(_mac[1]),_mac[1][9:]))
                    _rec["status"] = 0 
                    _rec["lifetime"] = 300
                    _rec["out_count"] = 0
                    _rec["in_count"] = 0
                    self.dev_list[_mac[0]] = _rec
                else:
                    if _mac[5] != self.dev_list[_mac[0]]['RSSI']:
                        print("\t%s <%s.%s.%s>:\t%s [%s] <-> %s [%s]" % (_mac[5],_mac[2],_mac[3],_mac[4],self.mac_format(_mac[0]),_mac[0][9:],self.mac_format(_mac[1]),_mac[1][9:]))
                        self.dev_list[_mac[0]]['RSSI'] = _mac[5]

                    self.dev_list[_mac[0]]['lifetime'] = 300

    def load_oui(self):
        f = open('oui.txt')
        while True:
            _l = f.readline()
            if len(_l) > 0:
                if "(hex)" in _l:
                    _t = _l.replace('(hex)','').replace('\t','').replace('\n','').replace('\r','').split('  ')
                    self.oui_list[_t[0]] = _t[1]
            else:
                break

    def mac_format(self, mac):
        _m = mac.replace(':', '-')
        if _m[0:8] in self.oui_list:
            return self.oui_list[_m[0:8]]


def Hex2Int(h):
    _v = "0123456789ABCDEF"
    _h = _v.index(h[0])
    _l = _v.index(h[1])
    return _h*16+_l


def main():
    global oui_list


    server =socketserver.TCPServer(("0.0.0.0", 64420),echorequestserver)
    server.serve_forever()


if __name__ == "__main__":

    main()

#
#
