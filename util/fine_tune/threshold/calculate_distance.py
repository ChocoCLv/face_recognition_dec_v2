import cv2
import sys
sys.path.append(sys.path[0] + '/..')
import facenet
import tensorflow as tf
import numpy as np
import os

pretrained_model_dir = '../pretrained_model/20180402-114759'

fine_tune_model_dir = '../models/20181108-140136'

facenet_model_checkpoint = pretrained_model_dir

testset_dir = '../dataset/testset_aligned'

trainset_dir = '../dataset/trainset_aligned'

debug_dir = '../dataset/debug'

dir_use = trainset_dir

distance_metric = 0

substract_mean = False

IMAGE_LIST = 'image_list_test.npy'
DIS_ARRAY = 'raw_distance_test.npy'


class Encoder:
    def __init__(self):
        self.sess = tf.Session()
        with self.sess.as_default():
            facenet.load_model(facenet_model_checkpoint)

    def generate_embedding(self, face):
        # Get input and output tensors
        images_placeholder = tf.get_default_graph().get_tensor_by_name(
            "input:0")
        embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
        phase_train_placeholder = tf.get_default_graph().get_tensor_by_name(
            "phase_train:0")

        prewhiten_face = facenet.prewhiten(face)

        # Run forward pass to calculate embeddings
        feed_dict = {
            images_placeholder: [prewhiten_face],
            phase_train_placeholder: False
        }
        embedding = self.sess.run(embeddings, feed_dict=feed_dict)[0]
        return embedding


class Person:
    def __init__(self, id):
        self.id = id
        self.embeddings = {}
        self.index_start = 0
        self.index_end = 0

    def add_sample_embedding(self, image_path, face_embedding):
        self.embeddings[image_path] = face_embedding

    def get_sample_embeddings(self):
        return self.embeddings

    def set_index(self, start, end):
        self.start = start
        self.end = end

    def get_index(self):
        return self.start, self.end


def load_encode_image(sample_dir, encoder):
    # 遍历./faces文件夹下的所有文件夹，即对应不同人员id的照片信息，子文件夹名即为人员id
    # 例如 文件夹./faces/1里存储了id为1的人员的照片
    persons = []
    dir_list = os.listdir(sample_dir)
    for i in range(0, len(dir_list)):
        path = os.path.join(sample_dir, dir_list[i])
        if os.path.isdir(path):
            person = Person(dir_list[i])
            image_list = os.listdir(path)
            for j in range(0, len(image_list)):
                image_path = os.path.join(path, image_list[j])
                image = cv2.imread(image_path)

                try:
                    face_embedding = encoder.generate_embedding(image)
                    person.add_sample_embedding(image_path, face_embedding)
                    print('encode: ', image_path)
                except Exception as e:
                    print('encode error: ' + str(e))

            persons.append(person)
    return persons


def check_disarray():
    distance_array = None
    persons = None
    image_list = None

    encoder = Encoder()
    persons = load_encode_image(dir_use, encoder)
    embeddings = {}  # key:path value:embedding
    for person in persons:
        start = len(embeddings)
        embeddings.update(person.get_sample_embeddings())
        end = len(embeddings)
        person.set_index(start, end)

    embeddings_list = list(embeddings.values())
    embedding_num = len(embeddings_list)

    distance_array = np.zeros((embedding_num, embedding_num))
    for i in range(embedding_num):
        distance_array[i, i] = 0
        for j in range(i + 1, embedding_num):
            embedding1 = [embeddings_list[i]]
            embedding2 = [embeddings_list[j]]
            distance = cal_distance(embedding1, embedding2)
            distance_array[i, j] = distance[0]
            distance_array[j, i] = distance[0]

    return distance_array, persons, embeddings


def gen_list_by_len(value, len):
    values = []
    for i in range(len):
        values.append(value)
    return values


def main():
    disarray, persons, embeddings = check_disarray()
    embeddings_list = list(embeddings.values())
    embedding_num = len(embeddings_list)
    class_num = len(persons)
    center_embeddings = []  # 存储所有的特征中心
    almost_center_embeddings = []  # 存储所有类别中距离特征中心最近的点
    radiuses = []  # 存储所有的最小类半径
    for person in persons:
        print(
            '.................................................................................'
        )
        print('calculate distance for ', person.id)
        tmp_array = np.matlib.zeros((embedding_num, embedding_num))
        # 根据person的索引范围可以取到disarray中对应的行，就能得到该类样本之间的距离
        start, end = person.get_index()
        tmp_array[start:end, :][:, start:end] = disarray[start:
                                                         end, :][:, start:end]
        # 计算类内的最大距离
        max_dis_in_class = tmp_array.max()
        max_loc = np.where(tmp_array == max_dis_in_class)
        print('max dis in class:', max_dis_in_class)

        # 找到具有最大距离的一对特征向量
        x = max_loc[0][0]
        y = max_loc[1][0]
        x_embedding = embeddings_list[x]
        y_embedding = embeddings_list[y]

        # 计算类内特征中心，以及最小覆盖半径
        center_embedding = (x_embedding + y_embedding) / 2
        radius = max_dis_in_class / 2  #不考虑误判
        center_embeddings.append(center_embedding)
        radiuses.append(radius)

        # 找出距离特征中心最近的点
        class_embeddings = person.get_sample_embeddings()
        embedding_num_in_class = len(class_embeddings)

        distances = cal_distance(
            gen_list_by_len(center_embedding, embedding_num_in_class),
            list(class_embeddings.values()))
        min_dis = min(distances)
        min_index = np.where(distances == min_dis)[0][0]
        print('min index: ', min_index)
        almost_center_embedding = list(class_embeddings.values())[min_index]
        almost_center_image_path = list(class_embeddings.keys())[min_index]
        almost_center_embeddings.append(almost_center_embedding)
        print('almost center image path: ', almost_center_image_path,
              ' distance: ', min_dis)
        print(
            '.................................................................................'
        )

    # 计算特征中心之间的距离
    center_dis_array = np.zeros((class_num,
                                 class_num))  # 存储不同特征中心的(距离/2)以及特征半径
    for i in range(class_num):
        center_dis_array[i][i] = radiuses[i]
        for j in range(i + 1, class_num):
            embedding1 = [center_embeddings[i]]
            embedding2 = [center_embeddings[j]]
            distance = cal_distance(embedding1, embedding2)
            center_dis_array[i][j] = distance[0] / 2
            center_dis_array[j][i] = distance[0] / 2

    print('actural center distance array:')
    print(center_dis_array)

    # 计算almost特征中心之间的距离
    almost_center_dis_array = np.zeros((class_num,
                                        class_num))  # 存储不同特征中心的(距离/2)以及特征半径
    for i in range(class_num):
        almost_center_dis_array[i][i] = radiuses[i]
        for j in range(i + 1, class_num):
            embedding1 = [almost_center_embeddings[i]]
            embedding2 = [almost_center_embeddings[j]]
            distance = cal_distance(embedding1, embedding2)
            almost_center_dis_array[i][j] = distance[0] / 2
            almost_center_dis_array[j][i] = distance[0] / 2
    print('almost center distance array:')
    print(almost_center_dis_array)


def test():
    times = 10
    image = cv2.imread(
        '/home/cl/deeplearning/demo/face_recognition_dec_v2/util/fine_tune/dataset/debug/1/1-900.png'
    )
    encoder = Encoder()
    embeddings = np.zeros((1, times))
    for i in range(times):
        embedding = encoder.generate_embedding(image)
        embeddings[0][i] = np.sum(embedding)

    print(embeddings)


def cal_distance(es1, es2):
    mean = 0
    if substract_mean:
        mean = np.mean(np.concatenate([es1, es2]), axis=0)

    distance = facenet.distance(
        np.array(es1) - mean, np.array(es2) - mean, distance_metric=distance_metric)

    return distance


if __name__ == '__main__':
    main()
