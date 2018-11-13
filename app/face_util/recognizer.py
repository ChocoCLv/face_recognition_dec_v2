import sys
sys.path.append(sys.path[0] + '/app')
sys.path.append(sys.path[0] + '/app/face_util')
import log
import settings
from detector import Detection
from encoder import Encoder
from face import Face

class Recognition:
    def __init__(self):
        self.sample_dir = settings.SAMPLE_DIR_RAW
        self.resize_factor = settings.RESIZE_FACTOR
        self.detect = Detection()
        self.encoder = Encoder()
        if settings.USE_SVM:
            from identifier_svm import Identifier
            print('load identifier_svm')
        else:
            from identifier_distance import Identifier
            print('load identifier_distance')
        self.identifier = Identifier()

    def identify(self, image):
        # 人脸检测
        st = log.get_current_time()
        faces = self.detect.find_faces(image)

        # 人脸识别
        for face in faces:
            # 人脸编码
            face.embedding = self.encoder.generate_embedding(face)
            # 人脸比对
            face.name = self.identifier.identify(face)

        et = log.get_current_time()
        log.logging.debug('recognition time: ' + str(et - st) + 'ms\n\n')
        return faces