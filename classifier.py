from art2m import ART2m


class Classifier:
    def __init__(self):
        self._classifier = ART2m()

    def train(self, vector: list, vector_type: int, avclass: str) -> None:
        self._classifier.f1(vector)
        recognition_type = self._classifier.f2g(s=vector, vector_type=vector_type, mode=0, avclass=avclass)

    def recognition(self, vector: list, vector_type=None) -> int:
        self._classifier.f1(vector)

        if vector_type:
            recognition_type = self._classifier.f2g(s=vector, vector_type=vector_type, mode=2)

        else:
            recognition_type = self._classifier.f2g(s=vector, mode=2)
        return recognition_type

    def unload_tree(self) -> None:
        self._classifier.tree.unload_tree()

    def load_tree(self, tree_filename: str) -> None:
        self._classifier.load_tree(tree_filename)

    def neurons_num_per_level(self) -> None:
        print('Количество нейронов на каждом уровне:', self._classifier.tree.neurons_num_per_level)

    def unload_tree_graph(self) -> None:
        self._classifier.tree.unload_tree_graph()
