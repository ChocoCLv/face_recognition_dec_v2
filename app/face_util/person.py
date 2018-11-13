class Person:
    def __init__(self, id):
        self.id = id
        self.embeddings = {}
        # 后续可以增加人员统计信息
    def add_sample_embedding(self, image_path, face_embedding):
        self.embeddings[image_path] = face_embedding

    def get_sample_embeddings(self):
        return self.embeddings