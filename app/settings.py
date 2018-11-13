# coding=utf-8
# 参数含义见《参数说明》
import os
################# 摄像头参数 ####################
USERNAME = 'admin'
CAMERA_NAME = 'CAMERA-1'
PASSWORD = 'admin123'
IP = '192.168.1.224'

################ 应用参数 ######################
SHOW_IMAGE = True #是否需要显示画面
ILLEGAL_ID = 'unknown'

LOG_BASE_DIR = '/tmp/dec'
LOG_FILE_PATH = LOG_BASE_DIR + '/log'
LOG_PHOTO_DIR = LOG_BASE_DIR + '/photo'
PHOTO_SAVE_DIR_LEGAL = LOG_PHOTO_DIR + '/legal'
PHOTO_SAVE_DIR_ILLEGAL = LOG_PHOTO_DIR + '/illegal'

#FACE_DIR = '/usr/local/share/applications/dec'
FACE_DIR = os.path.dirname(__file__) + '/..'
SAMPLE_DIR_RAW = FACE_DIR + '/faces/raw/'
SAMPLE_DIR_ENCODED = FACE_DIR + '/faces/encoded/'
RESULT_BUFFER_SIZE = 100

################ web端参数 ####################
WEB_SERVER_IP = '127.0.0.1'
WEB_SERVER_PORT = 2002
TYPE_RECOGNITION_RESULT = 1
TYPE_TASK_STATUS = 0
LEGAL = 1
ILLEGAL = 0
REPORT_PERIOD = 30 # 单位ms 

############### EMAIL告警参数 ################
EMAIL_ADDR = 'mingde_face@126.com'
EMAIL_SUPRESS_TIME = 2000  #单位 ms

################# 人脸检测参数 #################
RESIZE_FACTOR = 0.25
MINSIZE = 20
THRESHOLD = [0.6, 0.7, 0.7]
FACTOR = 0.709
FACE_CROP_MARGIN = 16

################ 人脸比对参数 ##################
USE_SVM = False
DISTANCE_THRESHOLD = 0.5
STRICT_DISTANCE_THRESHOLD = 0.2

############### PLC参数定义 ################
PLC_IP = '127.0.0.1'
PLC_PORT = 4321
# PLC开门后关门的延迟时间
# 单位：s
PLC_CLOSE_DELAY_TIME = 15
# 刷卡时间
PLC_TIME_OUT = 30
# 控制报文定义
door_ctl_msg = {}
# door No.1 control message
door_ctl_msg[1] = {}
door_ctl_msg[1]['open'] = b"\x01\x05\x00\x10\xff\x00\x8d\xff"
door_ctl_msg[1]['close'] = b"\x01\x05\x00\x10\x00\x00\xcc\x0f"
# door No.2 control message
door_ctl_msg[2] = {}
door_ctl_msg[2]['open'] = b"\x01\x05\x00\x11\xff\x00\xdc\x3f"
door_ctl_msg[2]['close'] = b"\x01\x05\x00\x11\x00\x00\x9d\xcf"
# door No.3 control message
door_ctl_msg[3] = {}
door_ctl_msg[3]['open'] = b"\x01\x05\x00\x12\x00\x00\x6d\xcf"
door_ctl_msg[3]['close'] = b"\x01\x05\x00\x12\xff\x00\x2c\x3f"
# door No.4 control message
door_ctl_msg[4] = {}
door_ctl_msg[4]['open'] = b"\x01\x05\x00\x13\xff\x00\x7d\xff"
door_ctl_msg[4]['close'] = b"\x01\x05\x00\x13\x00\x00\x3c\x0f"
door_ctl_msg['check'] = b'\x01\x01\x00\x00\x00\x04\x3D\xC9'

# opencv 属性值
# 0  CV_CAP_PROP_POS_MSEC Current position of the video file in milliseconds or video capture timestamp.
# 1  CV_CAP_PROP_POS_FRAMES 0-based index of the frame to be decoded/captured next.
# 2  CV_CAP_PROP_POS_AVI_RATIO Relative position of the video file: 0 - start of the film, 1 - end of the film.
# 3  CV_CAP_PROP_FRAME_WIDTH Width of the frames in the video stream.
# 4  CV_CAP_PROP_FRAME_HEIGHT Height of the frames in the video stream.
# 5  CV_CAP_PROP_FPS Frame rate.
# 6  CV_CAP_PROP_FOURCC 4-character code of codec.
# 7  CV_CAP_PROP_FRAME_COUNT Number of frames in the video file.
# 8  CV_CAP_PROP_FORMAT Format of the Mat objects returned by retrieve() .
# 9  CV_CAP_PROP_MODE Backend-specific value indicating the current capture mode.
# 10 CV_CAP_PROP_BRIGHTNESS Brightness of the image (only for cameras).
# 11 CV_CAP_PROP_CONTRAST Contrast of the image (only for cameras).
# 12 CV_CAP_PROP_SATURATION Saturation of the image (only for cameras).
# 13 CV_CAP_PROP_HUE Hue of the image (only for cameras).
# 14 CV_CAP_PROP_GAIN Gain of the image (only for cameras).
# 15 CV_CAP_PROP_EXPOSURE Exposure (only for cameras).
# 16 CV_CAP_PROP_CONVERT_RGB Boolean flags indicating whether images should be converted to RGB.
# 17 CV_CAP_PROP_WHITE_BALANCE_U The U value of the whitebalance setting (note: only supported by DC1394 v 2.x backend currently)
# 18 CV_CAP_PROP_WHITE_BALANCE_V The V value of the whitebalance setting (note: only supported by DC1394 v 2.x backend currently)
# 19 CV_CAP_PROP_RECTIFICATION Rectification flag for stereo cameras (note: only supported by DC1394 v 2.x backend currently)
# 20 CV_CAP_PROP_ISO_SPEED The ISO speed of the camera (note: only supported by DC1394 v 2.x backend currently)
# 21 CV_CAP_PROP_BUFFERSIZE Amount of frames stored in internal buffer memory (note: only supported by DC1394 v 2.x backend currently)

CV_CAP_PROP_FRAME_WIDTH = 3
CV_CAP_PROP_FRAME_HEIGHT = 4
CV_CAP_PROP_FPS = 5
CV_CAP_PROP_BUFFERSIZE = 21
