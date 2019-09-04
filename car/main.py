# -*- coding: utf-8 -*-
#
#

from pyb import Pin
from pyb import LED
import time

# Driver
# Front-left drive
Lf = Pin('Y2', Pin.OUT_PP)

# Back-left drive
Lb = Pin('Y1', Pin.OUT_PP)

# Front-right drive
Rf = Pin('Y3', Pin.OUT_PP)

# Back-right drive
Rb = Pin('Y4', Pin.OUT_PP)

# Rear sensor
Db = Pin('Y5', Pin.IN)

# Front-left sensor
Dl = Pin('Y6', Pin.IN)

# Front-middle sensor
Dm = Pin('Y7', Pin.IN)

# Front-right sensor
Dr = Pin('Y8', Pin.IN)


def stop():
    Lf.low()
    Lb.low()
    Rf.low()
    Rb.low()


def forward(ti):
    Lf.high()
    Lb.low()
    Rf.high()
    Rb.low()
    time.sleep_ms(ti)
    stop()


def start_over():
    for _t in [1, 5, 10, 20, 35, 50]:
        forward(_t)
        time.sleep_ms(10)


def back(ti):
    Lf.low()
    Lb.high()
    Rf.low()
    Rb.high()
    time.sleep_ms(ti)
    stop()


def left(ti):
    Lf.low()
    Lb.high()
    Rf.high()
    Rb.low()
    time.sleep_ms(ti)
    stop()


def right(ti):
    Lf.high()
    Lb.low()
    Rf.low()
    Rb.high()
    time.sleep_ms(ti)
    stop()


def get_status():
    return (Db.value(),
            Dl.value(),
            Dm.value(),
            Dr.value())


def show_led(v):
    for _i in [0, 1, 2, 3]:
        if v[_i] == 1:
            LED(_i+1).on()
        else:
            LED(_i+1).off()


def check_status(_st, chk):
    for _idx in [0, 1, 2, 3]:
        if chk[_idx] < 0:
            continue
        if chk[_idx] != _st[_idx]:
            return False
    return True


# Check
# For LED
show_led((1, 1, 1, 1))
time.sleep_ms(1000)
show_led((1, 1, 0, 0))
time.sleep_ms(1000)
show_led((0, 0, 1, 1))
time.sleep_ms(1000)

# For Driver
forward(10)
time.sleep_ms(500)
back(10)
time.sleep_ms(500)
left(10)
time.sleep_ms(500)
right(10)
time.sleep_ms(500)


# Number of to try
"""考虑：实现过程中的动态机动特性"""
try_n = 0
# Last status of Sensors
st_old = None
# Status of running
FORWARD = 1
LEFT = 2
RIGHT = 3
STOP = 4
BACK = 5

status = STOP

while True:
    st = get_status()
    show_led(st)
    if check_status(st, [-1, 1, 1, 1]):
        # without obstacles
        if status == 0:
            start_over()
            status = FORWARD
        else:
            forward(50+try_n*10)
    else:
        stop()
        status = STOP
        if check_status(st, [0, -1, 0, -1]):
            continue
        else:
            if check_status(st, [1, -1, 0, -1]) or check_status(st, [1, 0, -1, 0]):
                # with front-end obstacles
                back(80)
                left(50+try_n*10)
                status = BACK
            elif check_status(st, [-1, 0, -1, 1]):
                # with front-left obstacles
                right(50+try_n*10)
                status = RIGHT
            elif check_status(st, [-1, 1, -1, 0]):
                # with front-right obstacles
                left(50+try_n*10)
                status = RIGHT

        """过程动态机动策略及其实现，待验证"""
        if status < STOP and st_old == st:
            """状态没有改变"""
            if try_n < 3:
                """加快脱离现在的状态"""
                try_n += 1
        else:
            try_n = 0
            st_old = st

    time.sleep_ms(10)

#
#
