from json import loads
from time import time

from classifier import Classifier
from preanalyze import file_vectorization


class Dataset:
    def __init__(self):
        self.vectors = []
        self.types = []
        self.matrix = []
        self.predicted_type = []
        self.avclasses = []
        self.classifier = Classifier()

    def _reset(self) -> None:
        """Очистка данных"""
        self.types.clear()
        self.avclasses.clear()
        self.vectors.clear()
        self.predicted_type.clear()
        self.matrix.clear()

    def train_vectors_ember(self, root: str, num_of_images=None) -> None:
        """Получение вектора гистограмм и типов из EMBER"""
        self._reset()
        files = ['train_features_' + str(i) + '.jsonl' for i in range(6)]
        for filename in files:
            print('Обучение на части датасета', filename)
            file = open(root + filename)
            index = 0
            for line in file:
                data = loads(line)
                if num_of_images:
                    if index > num_of_images - 1:
                        break
                vector_type = data['label']
                if vector_type != -1:
                    vector = [data['header']['optional']['major_image_version'],
                              data['header']['optional']['minor_image_version'],
                              data['header']['optional']['minor_linker_version'],
                              data['header']['optional']['major_linker_version'],
                              data['header']['optional']['major_operating_system_version'],
                              data['header']['optional']['minor_operating_system_version']]
                    vector += data['histogram']
                    self.classifier.train(vector, vector_type, data['avclass'])
                    index += 1
            file.close()
        self.classifier.unload_tree()
        print('Обучение окончено')

    def recognition_vectors(self, changed_files: dict, tree_filename: str) -> None:
        self._reset()
        self.classifier.load_tree(tree_filename)
        start = time()
        for filename in changed_files.keys():
            vector = changed_files[filename]
            recognition_type = self.classifier.recognition(vector)
        end = time()
        print('Время распознавания', end - start)

    def recognition_vector(self, filename: str, tree_filename: str) -> None:
        self._reset()
        self.classifier.load_tree(tree_filename)
        vector = file_vectorization(filename)
        recognition_type = self.classifier.recognition(vector)
        if recognition_type == 1:
            print('Файл', filename, 'был распонан как вредоносный')
        else:
            print('Файл ', filename, ' был распознан как безвредный')

    def additional_training(self, filename: str, tree_filename: str) -> None:
        self._reset()
        self.classifier.load_tree(tree_filename)
        file = open(filename, 'r')
        for line in file:
            data = loads(line)
            self.classifier.train(data['vector'], data['type'], data['avclass'])
        file.close()
        print('Количество нейронов на каждом уровне:', self.classifier.neurons_num_per_level)
        self.classifier.unload_tree()
        print('Обучение окончено')

    def _prepare_vectors_ember(self, root: str, num_of_images: int) -> None:
        self._reset()
        files = [root+'train_features_' + str(i) + '.jsonl' for i in range(6)]
        for filename in files:
            file = open(filename)
            index = 0

            for line in file:
                data = loads(line)
                if index < num_of_images:
                    label = data['label']
                    if label != -1:
                        vector = []
                        avclass = data['avclass']
                        histogram = data['histogram']
                        vector.append(data['header']['optional']['major_image_version'])
                        vector.append(data['header']['optional']['minor_image_version'])
                        vector.append(data['header']['optional']['minor_linker_version'])
                        vector.append(data['header']['optional']['major_linker_version'])
                        vector.append(data['header']['optional']['major_operating_system_version'])
                        vector.append(data['header']['optional']['minor_operating_system_version'])
                        vector += histogram
                        index += 1
                        self.vectors.append(vector)
                        self.types.append(label)
                        self.avclasses.append(avclass)

            file.close()

    def vectors_to_file(self, num_of_images: int) -> None:
        """Запись датасета в файлы для обучения модуля на С++"""
        root = 'ember2018/'
        self._prepare_vectors_ember(root, num_of_images)
        histo_file = open('vectors/train_histograms.txt', 'w')
        num_of_vectors = len(self.vectors)
        histo_file.write(str(int(num_of_vectors * 2)) + ' ' + str(len(self.vectors[0])) + ' ')
        for i in range(2):
            for s, type in zip(self.vectors, self.types):
                for i in s:
                    histo_file.write(str(i) + ' ')

                if type == 0:
                    histo_file.write('benign ')
                else:
                    histo_file.write('malicious ')
            self.vectors.reverse()
            self.types.reverse()
        histo_file.close()
