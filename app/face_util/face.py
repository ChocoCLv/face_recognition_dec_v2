import sys
sys.path.append(sys.path[0] + '/app')
from recognition_result_processor import Result

class Face:
    def __init__(self):
        self.name = None
        self.bounding_box = None
        self.image = None  #人脸部分
        self.face_image_raw = None #原始人脸部分
        self.image_raw = None  #原始分辨率图片
        self.image_small = None  #缩放后便于处理的图片
        self.embedding = None
        self.result = Result()