# coding=utf-8
import logging
import settings
import cv2
import time
import os

def check_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

check_dir(settings.LOG_BASE_DIR)
check_dir(settings.LOG_PHOTO_DIR)
check_dir(settings.PHOTO_SAVE_DIR_ILLEGAL)
check_dir(settings.PHOTO_SAVE_DIR_LEGAL)
check_dir(settings.SAMPLE_DIR_ENCODED)

try:
    os.remove(settings.LOG_FILE_PATH)
except:
    print('no log file')

logging.basicConfig(
    filename=settings.LOG_FILE_PATH,
    format=
    '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG)


def save_photo(image, id, timestamp, distance):
    if distance > settings.DISTANCE_THRESHOLD:
        path = settings.PHOTO_SAVE_DIR_ILLEGAL
    else:
        path = settings.PHOTO_SAVE_DIR_LEGAL
    file_name = str(id) + '_' + str(timestamp) + '_' + str(distance) + '.jpg'
    file_path = path + os.path.sep + file_name
    logging.info('save photo: ' + file_path)
    cv2.imwrite(file_path, image)

    if (distance < settings.STRICT_DISTANCE_THRESHOLD):
        add_sample_photo(image, id, file_name)

    return file_path


def add_sample_photo(image, id, file_name):
    file_path = settings.SAMPLE_DIR_RAW + os.path.sep + id + os.path.sep + file_name
    logging.info('add_sample_photo: ' + file_path)
    cv2.imwrite(file_path, image)


def get_current_time():
    return int(round(time.time() * 1000))
