import pickle
import os
from face import Face
import numpy as np
import sys
sys.path.append(sys.path[0] + '/app')
import log

classifier_model = os.path.dirname(__file__) + "/classifier.pkl"

class Identifier:
    def __init__(self):
        print('load svm')
        with open(classifier_model, 'rb') as infile:
            self.model, self.class_names = pickle.load(infile)

    def identify(self, face):
        if face.embedding is not None:
            predictions = self.model.predict_proba([face.embedding])
            best_class_indices = np.argmax(predictions, axis=1)
            log.logging.info(predictions)
            return self.class_names[best_class_indices[0]]