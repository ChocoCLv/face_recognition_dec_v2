import os
import time
import numpy as np
import tensorflow as tf
import sys
sys.path.append(sys.path[0] + '/app')
import log
from face import Face
import facenet

facenet_model_checkpoint = os.path.dirname(__file__) +'/model_checkpoints'


class Encoder:
    def __init__(self):
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.7)
        self.sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
        with self.sess.as_default():
            facenet.load_model(facenet_model_checkpoint)

    def generate_embedding(self, face):
        st = log.get_current_time()
        # Get input and output tensors
        images_placeholder = tf.get_default_graph().get_tensor_by_name(
            "input:0")
        embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
        phase_train_placeholder = tf.get_default_graph().get_tensor_by_name(
            "phase_train:0")

        #prewhiten_face = facenet.prewhiten(face.image)
        prewhiten_face = facenet.prewhiten(face.face_image_raw)
        # Run forward pass to calculate embeddings
        feed_dict = {
            images_placeholder: [prewhiten_face],
            phase_train_placeholder: False
        }
        embedding = self.sess.run(embeddings, feed_dict=feed_dict)[0]
        et = log.get_current_time()
        log.logging.debug('encoding time: ' + str(et - st) + 'ms')
        return embedding