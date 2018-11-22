import pickle
import os
from face import Face
import numpy as np
import sys
sys.path.append(sys.path[0] + '/app')
import log
import settings

classifier_model = os.path.dirname(__file__) + "/classifier.pkl"


class Identifier:
    def __init__(self):
        print('load svm')
        with open(classifier_model, 'rb') as infile:
            self.model, self.class_names = pickle.load(infile)
            log.logging.info(self.class_names)

    def identify(self, face):
        if face.embedding is not None:
            predictions = self.model.predict_proba([face.embedding])
            best_class_indices = np.argmax(predictions, axis=1)
            log.logging.info(predictions)
            prediction = predictions[0][best_class_indices[0]]
            face.result.min_distance = prediction
            if prediction > settings.SVM_SIMILARITY_THRESHOLD:
                face.result.id = self.class_names[best_class_indices[0]]
                face.result.result = settings.LEGAL
            else:
                face.result.id = settings.ILLEGAL_ID
                face.result.result = settings.ILLEGAL

            log.save_debug_photo(face.face_image_raw, face.result.id,
                                 face.result.timestamp, prediction)

            face.result.file_path = log.save_photo(
                face.image_raw, face.result.id, face.result.timestamp,
                prediction)
            return face.result.id
