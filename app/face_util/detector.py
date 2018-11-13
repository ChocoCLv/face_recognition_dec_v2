import align.detect_face
import tensorflow as tf
import sys
sys.path.append('/..')
from scipy import misc
import settings
import log
from face import Face
import cv2
import numpy as np

class Detection:
    # face detection parameters
    minsize = settings.MINSIZE
    threshold = settings.THRESHOLD
    factor = settings.FACTOR

    def __init__(self, face_crop_size=160):
        self.pnet, self.rnet, self.onet = self._setup_mtcnn()
        self.face_crop_size = face_crop_size
        self.face_crop_margin = settings.FACE_CROP_MARGIN

    def _setup_mtcnn(self):
        with tf.Graph().as_default():
            sess = tf.Session()
            with sess.as_default():
                return align.detect_face.create_mtcnn(sess, None)

    def find_faces(self, image_raw):
        st = log.get_current_time()
        faces = []
        image_small = cv2.resize(
            image_raw, (0, 0),
            fx=settings.RESIZE_FACTOR,
            fy=settings.RESIZE_FACTOR)
        bounding_boxes, _ = align.detect_face.detect_face(
            image_small, self.minsize, self.pnet, self.rnet, self.onet,
            self.threshold, self.factor)
        for bb in bounding_boxes:
            face = Face()
            face.image_raw = image_raw
            face.bounding_box = np.zeros(4, dtype=np.int32)

            img_size = np.asarray(image_small.shape)[0:2]
            face.bounding_box[0] = np.maximum(
                bb[0] - self.face_crop_margin / 2, 0)
            face.bounding_box[1] = np.maximum(
                bb[1] - self.face_crop_margin / 2, 0)
            face.bounding_box[2] = np.minimum(
                bb[2] + self.face_crop_margin / 2, img_size[1])
            face.bounding_box[3] = np.minimum(
                bb[3] + self.face_crop_margin / 2, img_size[0])
            cropped = image_small[face.bounding_box[1]:face.bounding_box[3],
                                  face.bounding_box[0]:face.bounding_box[2], :]
            face.image = misc.imresize(
                cropped, (self.face_crop_size, self.face_crop_size),
                interp='bilinear')
            face.result.timestamp = log.get_current_time()
            faces.append(face)

        et = log.get_current_time()
        log.logging.debug('face num: ' + str(len(faces)) + ' time usage:' +
                          str(et - st) + 'ms')
        return faces