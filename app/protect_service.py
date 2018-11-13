# coding=utf-8
import subprocess
import settings
import socket
import json
import time
# error code为一个字节，若某个服务不存在，则将对应的bit置为1
# 服务名称                       |   对应的bit位  |  
# real_time_face_recognition    |     0         |   0x01
# sshd                          |     1         |   0x02

services = {'real_time_face_recognition':0x01, 'sshd':0x02}

def execute_command(cmd):
    s = subprocess.Popen(
        str(cmd), stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    stderrinfo, stdoutinfo = s.communicate()
    res = (str(stderrinfo) + str(stdoutinfo)).split('\\n')
    return s.returncode, res

def check_service():
    ret,ps = execute_command('ps -ef')
    ps_str = str(ps)
    error=0x00
    for service in services:
        if ps_str.find(service)==-1:
            error|=services[service]
    return error

def report_error(error):
    msg = {}
    msg['type']=0
    msg['error']=error
    msg_json = json.dumps(msg)
    print(msg_json)
    bs = bytes(msg_json+'\n', encoding="utf8")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((settings.WEB_SERVER_IP,settings.WEB_SERVER_PORT))
        sock.send(bs)
    except Exception as e:
        print(str(e))
    finally:
        sock.close()

if __name__=='__main__':
    while True:
        err = check_service()
        report_error(err)
        time.sleep(settings.REPORT_PERIOD)# every 30min
