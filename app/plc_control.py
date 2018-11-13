# PLC通信进程 在需要开门时会启动该进程
# 正常开门或者超时后还未检测到刷卡信号结束进程

import log
import threading
import settings
import socket
import time
from queue import Queue

class PLCControl:
    def __init__(self):
        self.door = None
        self.is_reset = False
        self.is_run = False
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.start_process, args=())
        self.thread.start()

    def close_door(self):
        self.connect_to_server()
        log.logging.info('time out, close door')
        try:
            self.plc_sock.send(settings.door_ctl_msg[self.door]['close'])
        except Exception as e:
            log.logging.error(str(e))
        self.plc_sock.close()

    def check_door(self):
        self.connect_to_server()
        seconds = 0
        self.door = -1
        while seconds <= settings.PLC_TIME_OUT:
            self.plc_sock.send(settings.door_ctl_msg['check'])
            door_status = self.plc_sock.recv(1024)
            # check which door should be opened
            if door_status[3] == 0x01:
                self.door = 1
                break
            elif door_status[3] == 0x02:
                self.door = 2
                break
            elif door_status[3] == 0x04:
                self.door = 3
                break
            elif door_status[3] == 0x10:
                self.door = 4
                break
            elif door_status[3] == 0x00:
                log.logging.debug('all door closed')
            seconds = seconds + 0.1
            time.sleep(0.1)
            log.logging.debug('check door:'+str(seconds))

            if self.is_reset == True:
                self.is_reset = False
                seconds = 0
                log.logging.debug('reset in check_door')
        self.plc_sock.close()

    def open_door(self):
        if self.is_run:
            self.reset()
        else:
            self.lock.release()
            self.is_run = True

    def connect_to_server(self):
        self.plc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.plc_sock.connect((settings.PLC_IP, settings.PLC_PORT))
        except Exception as e:
            log.logging.error(str(e))

    def start_process(self):
        self.lock.acquire()
        while True:
            self.lock.acquire()
            #self.check_door()
            self.door = 1
            if self.door == -1:
                self.is_run = False
                continue

            log.logging.info('open door: No.' + str(self.door))
            self.connect_to_server()
            try:
                self.plc_sock.send(settings.door_ctl_msg[self.door]['open'])
            except Exception as e:
                log.logging.error(str(e))
                self.is_run = False
                continue
            self.plc_sock.close()

            seconds = 0
            while seconds < settings.PLC_CLOSE_DELAY_TIME:
                if self.is_reset == True:
                    self.is_reset = False
                    seconds = 0
                time.sleep(0.2)
                seconds = seconds+0.2
                
            self.close_door()
            self.is_run = False

    def reset(self):
        log.logging.debug('reset open door process')
        self.is_reset = True


if __name__ == '__main__':
    plc = PLCControl()
    plc.open_door()
    time.sleep(1)
    plc.open_door()
    time.sleep(5)
    plc.open_door()
