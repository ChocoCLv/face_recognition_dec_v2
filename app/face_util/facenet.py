# coding=utf-8

import os
import tensorflow as tf
import numpy as np
from tensorflow.python.platform import gfile
import math
import re
import log

def prewhiten(x):
    mean = np.mean(x)
    std = np.std(x)
    std_adj = np.maximum(std, 1.0 / np.sqrt(x.size))
    y = np.multiply(np.subtract(x, mean), 1 / std_adj)
    return y


def load_model(model, input_map=None):
    # Check if the model is a model directory (containing a metagraph and a checkpoint file)
    #  or if it is a protobuf file with a frozen graph
    model_exp = os.path.expanduser(model)
    if (os.path.isfile(model_exp)):
        log.logging.info('Model filename: ' + model_exp)
        with gfile.FastGFile(model_exp, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, input_map=input_map, name='')
    else:
        log.logging.info('Model directory: ' + model_exp)
        meta_file, ckpt_file = get_model_filenames(model_exp)

        log.logging.info('Metagraph file: ' + meta_file)
        log.logging.info('Checkpoint file: ' + ckpt_file)

        saver = tf.train.import_meta_graph(
            os.path.join(model_exp, meta_file), input_map=input_map)
        saver.restore(tf.get_default_session(),
                      os.path.join(model_exp, ckpt_file))


def distance(embedding, known_face_embeddings):
    dists =  []
    for key in  known_face_embeddings:
        known_face_embedding = known_face_embeddings[key]
        # Euclidian distance
        diff = np.subtract(embedding, known_face_embedding)
        dist = np.sum(np.square(diff))
        dists.append(dist)
        log.logging.info("compare to "+key+", euclidian distance: "+str(dist))
    return dists


def get_model_filenames(model_dir):
    files = os.listdir(model_dir)
    meta_files = [s for s in files if s.endswith('.meta')]
    if len(meta_files) == 0:
        raise ValueError(
            'No meta file found in the model directory (%s)' % model_dir)
    elif len(meta_files) > 1:
        raise ValueError(
            'There should not be more than one meta file in the model directory (%s)'
            % model_dir)
    meta_file = meta_files[0]
    ckpt = tf.train.get_checkpoint_state(model_dir)
    if ckpt and ckpt.model_checkpoint_path:
        ckpt_file = os.path.basename(ckpt.model_checkpoint_path)
        return meta_file, ckpt_file

    meta_files = [s for s in files if '.ckpt' in s]
    max_step = -1
    for f in files:
        step_str = re.match(r'(^model-[\w\- ]+.ckpt-(\d+))', f)
        if step_str is not None and len(step_str.groups()) >= 2:
            step = int(step_str.groups()[1])
            if step > max_step:
                max_step = step
                ckpt_file = step_str.groups()[0]
    return meta_file, ckpt_file