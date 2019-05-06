# -*- coding: UTF-8 -*-
#
# AI@Home
# =======
# Version: 0.8
#
# 2019.1.12 @Home
# ---------------
#
# 1）从AI@Home/CC上接收探针数据，并判断是否有告警，若有，则发送告警邮件；
# 2）准点（凌晨2点、早晚8点、晚上11点）发送邮件，确认本程序在运行（表示：程序在工作，或没有停电）。
#
#

import time
import serial
import datetime
import snd_mail

device = {}

alarm_info = ""

send_st = 0


def Hex2Int(h):
    _v = "0123456789ABCDEF"
    _h = _v.index(h[0])
    _l = _v.index(h[1])
    return _h*16+_l


def DisplayValue(mac, dev):

    global alarm_info, send_st

    _alarm = False

    _str = ""
    
    _str += str(datetime.datetime.now())
    _str += " > %s %s" % (mac, dev['Name'])

    if 'Data' in dev:

        _state = int(dev['Data'][:2])
        # _step = int(dev['Data'][2:4])
        if send_st == 0:
            _step = 2
        else:
            _step = 0

        print "_state: ", _state, "_step: ", _step

        _temp = Hex2Int(dev['Data'][4:6])
        _temp_l = Hex2Int(dev['Data'][6:8])
        _rh = Hex2Int(dev['Data'][8:10])

        if _state == 1:
            _str += "\tNo alarm!"
            send_st = 0
        else:
            if _step > 0:
                _str += "\tAlarm[%d]" % _step
                if _step == 2:
                    """在进入状态2时报警"""
                    _alarm = True
                    send_st = 1
            else:
                return False

        # _str += "\tT: %d.%d, RH: %d%%" % (_temp, _temp_l, _rh)

    if "Str" not in dev:

        dev['Str'] = ""

    if _str[27:] not in dev['Str']: 
        f = open("rec.txt", "a")
        f.write(_str+"\n")
        dev['Str'] = _str
        f.close()

    if _alarm:
        alarm_info = _str

    print(_str)

    return _alarm


def DisplayDevice():

    _alarm = False

    for _d in device:

        if not device[_d].has_key('Name'):
            continue

        if 'AI@Home' in device[_d]['Name']:
           if DisplayValue(_d, device[_d]):
               _alarm = True

    return _alarm


def Handler(adv_type, data):

    if len(data) < 6:
        return False

    print("adv_type: %c" % adv_type)
    print("data: ",data)
    param = data.replace('\r','').replace('\n','').split('^')
    print("param: ",param)

    if adv_type == 'N':
        print "Name: ",data
        if len(param)==3 and param[1] not in device:
            device[param[1]] = {}
            device[param[1]]['Name'] = param[0]
    else:
        print "param: ",param
        if len(param)==3 and param[1] in device:
            device[param[1]]['Data'] = param[0]
        else:
            device[param[1]] = {}
            device[param[1]]['Name'] = 'AI@Home'


    return DisplayDevice()

    
def main():

    global alarm_info

    _mail_sent = False
    # ser = serial.Serial('/dev/tty.usbmodem3470365F30372', 9600)
    # ser = serial.Serial('/dev/tty.usbserial-1470', 9600)
    ser = serial.Serial('COM3', 9600)
    mail = snd_mail.MailAlarm(passwd="196512shenwei")

    mail.sendmail(body="Alarm", html="<b>Application Started.</b>")
    data = ''

    state = 0
    adv_type = ''
    _c = ''

    _ret = False

    while 1:

        while ser.inWaiting() > 0:

            _n_c = _c
            _c = ser.read(1)

            # print _c, ' ', state

            if state == 0:
                if _c == 'D' or _c == 'N':
                    adv_type = _c
                    state = 1
                    _mail_sent = False
            elif state == 1:
                if _c == ':':
                    state = 2
            elif state == 2:
                data += _c

                if _c == '\r':
                    _ret = Handler(adv_type, data)
                    data = ''
                    state = 0
                if _c == ':' and _n_c != 'I':
                    adv_type = _n_c
                    _ret = Handler(adv_type, data[-2])
                    data = ''

                if adv_type == 'D' and _ret and not _mail_sent:
                    """发送报警邮件"""
                    mail.sendmail(body="Alarm", html="<b>["+alarm_info+"]</b>")
                    _mail_sent = True
            else:
                state = 0

        _ti = datetime.datetime.now()
        if _ti.hour in [2, 8, 20, 23] and _ti.minute == 0 and _ti.second == 0:
            """发送通报信息"""
            mail.sendmail(body="Notification", html="<b>Info: application %s be alive!</b>" % str(_ti))
            time.sleep(1)


if __name__ == "__main__":

    main()

#
#
