import os
from face import Face
import numpy as np
import sys
sys.path.append('/..')
import settings
from person import Person
import log
import facenet

class Identifier:
    def __init__(self):
        self.sample_dir = settings.SAMPLE_DIR_RAW
        self.persons = self.load_encode_image()
        print('load sample image')

    def identify(self, face):
        if face.embedding is not None:
            st = log.get_current_time()
            total_min_distance = 100
            min_id = settings.ILLEGAL_ID

            # See if the face is a match for the known face(s)
            for person in self.persons:
                distances = list(
                    facenet.distance(face.embedding,
                                     person.get_sample_embeddings()))
                min_dist = min(distances)
                if min_dist < total_min_distance:
                    total_min_distance = min_dist
                    min_id = person.id

            face.result.id = min_id
            face.result.min_distance = total_min_distance

            if total_min_distance > settings.DISTANCE_THRESHOLD:
                min_id = settings.ILLEGAL_ID
                face.result.result = settings.ILLEGAL
            else:
                face.result.result = settings.LEGAL

            et = log.get_current_time()
            log.logging.debug('identify time: ' + str(et - st) + 'ms')
            log.logging.info('identify result: ' + min_id)

            face.result.file_path = log.save_photo(
                face.image_raw, face.result.id, face.result.timestamp,
                total_min_distance)
            return min_id

    # 更新人脸标准库
    def load_encode_image(self):
        # 遍历./faces文件夹下的所有文件夹，即对应不同人员id的照片信息，子文件夹名即为人员id
        # 例如 文件夹./faces/1里存储了id为1的人员的照片
        persons = []
        dir_list = os.listdir(self.sample_dir)
        for i in range(0, len(dir_list)):
            path = os.path.join(self.sample_dir, dir_list[i])
            if os.path.isdir(path):
                person = Person(dir_list[i])
                image_list = os.listdir(path)
                for j in range(0, len(image_list)):
                    image_path = os.path.join(path, image_list[j])
                    encode_path = settings.SAMPLE_DIR_ENCODED + image_list[
                        j].split('.')[0] + '.npy'
                    encode_dir = os.path.dirname(encode_path)
                    log.check_dir(encode_dir)
                    log.logging.info('load image: ' + image_path)

                    if os.path.exists(encode_path):
                        log.logging.info('encoded file exists: ' + encode_path)
                        face_embedding = np.load(encode_path)
                        person.add_sample_embedding(image_path, face_embedding)
                        continue

                    image = cv2.imread(image_path)

                    try:
                        face = self.detect.find_faces(image)[0]
                        face_embedding = self.encoder.generate_embedding(face)
                        person.add_sample_embedding(image_path, face_embedding)
                        np.save(encode_path, face_embedding)
                        log.logging.info('save encode file to ' + encode_path)
                    except Exception as e:
                        log.logging.error(str(e))
                        os.remove(image_path)

                persons.append(person)
        return persons