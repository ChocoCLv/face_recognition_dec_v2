import settings
import json
import log
import socket
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import time
from protect_service import execute_command

msg_queue = []
last_result = None
executor = ProcessPoolExecutor()
msg_queue = []
result_time_map = {}  #{id,time_stamp}

tasks = []


def put_result(result):
    if len(msg_queue) == settings.RESULT_BUFFER_SIZE:
        del msg_queue[0]

    msg_queue.append(result.to_json())
    last_result = result.to_json()


def push_result():
    log.logging.info('try to push result')
 
    if len(msg_queue)==0:
        return

    task = executor.submit(_push_result)
    log.logging.info('push result return')
    msg_queue.clear()


def _push_result():
    log.logging.info('push result')
    time.sleep(3)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    log.logging.debug(msg_queue)
    try:
        sock.connect((settings.WEB_SERVER_IP, settings.WEB_SERVER_PORT))
        msg_json = json.dumps(msg_queue)
        bs = bytes(msg_json + '\n', encoding="utf8")
        sock.send(bs)
        log.logging.debug('send recognition result successfully')
        return None
    except Exception as e:
        log.logging.error(str(e))
        return msg_queue
    finally:
        sock.close()


def send_email(result):
    log.logging.debug('try to send email()')
    if email_send_filter(result):
        executor.submit(_send_email,result)
        log.logging.debug('send email return')


def _send_email(result):
    log.logging.debug('send email')
    desc = ''
    if result.result == settings.LEGAL:
        desc = '识别正常'
    else:
        desc = '识别异常'
    cmd = 'echo "' + settings.CAMERA_NAME + '"| mail -s "' + desc + '" -A ' + result.file_path + ' ' + settings.EMAIL_ADDR
    # execute_command(cmd)
    log.logging.debug('send email over')


def email_send_filter(result):
    if(result.id == settings.ILLEGAL_ID):
        return True
    if (result_time_map.get(result.id, None) is None):
        result_time_map[result.id] = result.timestamp
        return True

    time_interval = result.timestamp - result_time_map[result.id]
    if time_interval < settings.EMAIL_SUPRESS_TIME:
        log.logging.info('supress result in '+str(time_interval)+'ms')
        return False
    else:
        result_time_map[result.id] = result.timestamp
        return True


class Result:
    def __init__(self):
        self.id = None
        self.timestamp = None
        self.result = None
        self.min_distance = None
        self.file_path = None

    def to_json(self):
        return {
            'type': settings.TYPE_RECOGNITION_RESULT,
            'id': str(self.id),
            'result': str(self.result),
            'time': str(self.timestamp),
            'distance': str(self.min_distance),
            'path': str(self.file_path),
            'camera': settings.CAMERA_NAME
        }


if __name__ == '__main__':
    r = Result()
    r.id = 'test1'
    r.min_distance = 0.1
    r.timestamp = log.get_current_time()
    r.result = 1
    r.file_path = '/tmp/test.jpg'
    put_result(r)
    push_result()
    send_email(r)
    r.timestamp = log.get_current_time()
    send_email(r)
    r.id='test2'
    send_email(r)
    time.sleep(3)
    r.timestamp = log.get_current_time()
    send_email(r)
