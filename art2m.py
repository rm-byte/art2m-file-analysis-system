from datetime import datetime
from json import load
from scipy.linalg import norm

from logs import write_logs
from neuron import Y
from tree import Tree


class ART2m:
    def __init__(self, filename=None):
        self.mode = None  # 0 - обучение, 1 - дообучение, 2 - распознавание
        self._parameter_a = 1
        self._parameter_b = 1
        self._parameter_c = 0.2
        self.parameter_d = 0.99
        self._parameter_e = 0.000001
        self._theta = 0.0001

        self.vector_s = None
        self.n = None
        self._vector_u = []
        self._vector_w = []
        self._vector_x = []
        self._vector_v = []
        self._vector_p = []
        self._vector_q = []
        self._vector_r = []
        if filename:
            filename = 'tree/tree_parameters_' + str(datetime.now().date()) + '.txt'
            self.tree = self.load_tree(filename)
        else:
            self.tree = Tree()

    def _step_w(self) -> None:
        self._vector_w = [i + self._parameter_a * j for i, j in zip(self.vector_s, self._vector_u)]

    def _step_x(self) -> None:
        WN = norm(self._vector_w)
        denom = self._parameter_e + WN
        self._vector_x = [i / denom for i in self._vector_w]

    def _step_v(self) -> None:
        self._vector_v = [self._threshold_function(i) + self._parameter_b * self._threshold_function(j) for i, j in
                          zip(self._vector_x, self._vector_q)]

    def _step_u(self) -> None:
        vn = norm(self._vector_v)
        denom = self._parameter_e + vn
        self._vector_u = [i / denom for i in self._vector_v]

    def _step_p(self) -> None:
        self._vector_p = [i for i in self._vector_u]

    def _step_q(self) -> None:
        pn = norm(self._vector_p)
        denom = self._parameter_e + pn
        self._vector_q = [i / denom for i in self._vector_p]

    def _threshold_function(self, x: float) -> float:
        if x > self._theta:
            return x
        return 0

    def _set_to_zero(self) -> None:
        vectors = [self._vector_u, self._vector_w, self._vector_x, self._vector_v, self._vector_p, self._vector_q,
                   self._vector_r]
        for vector in vectors:
            vector.clear()
            for i in range(self.n):
                vector.append(0)

    def f1(self, vector: list) -> None:
        self.vector_s = vector
        self.n = len(self.vector_s)
        self._set_to_zero()

        for i in range(2):
            self._step_w()
            self._step_x()
            self._step_v()
            self._step_u()
            self._step_p()
            self._step_q()

    def _step_r(self) -> None:
        un = norm(self._vector_u)
        pn = norm(self._vector_p)
        denom = self._parameter_e + un + self._parameter_c * pn
        self._vector_r = [(i + self._parameter_c * j) / denom for i, j in zip(self._vector_u, self._vector_p)]

    def _step_p2(self, y: Y) -> None:
        self._vector_p = [i + j * self.parameter_d for i, j in zip(self._vector_u, y.z_weight)]

    def _create_neurons(self, vector_type: int, avclass: str) -> None:
        while not self.tree.is_last_level():
            self.tree.create_neuron(vector_type, avclass)
            self.tree.set_meta(self.tree.y_current)
            self.tree.step_y(self._vector_p)
            self.tree.step_z(y=self.tree.y_current, i_max=-1, d=self.parameter_d, u=self._vector_u)

    def f2g(self, s: list, mode: int, vector_type=None, avclass=None) -> (int, int):
        self.mode = mode
        self.vector_s = s
        self.tree.set_n(self.n)
        if self.tree.current_level == 0 and self.tree.y_current is None:
            self.tree.create_root()
            self.tree.step_y(self._vector_p)
            self.tree.step_z(y=self.tree.y_current, i_max=-1, d=self.parameter_d, u=self._vector_u)
            self.tree.set_meta(self.tree.y_current)
            self._create_neurons(vector_type, avclass)

        if self.tree.current_level == 0:
            self.tree.unfreeze()
            y = self.tree.root
            y.y_value = 0
            for i, j in zip(y.z_weight, self._vector_p):
                y.y_value += i * j
            self._step_p2(y)

        while self.tree.current_level < self.tree.kc - 1 and not self.tree.is_all_freeze():
            self.tree.step_y(self._vector_p)
            i_max, y_max = self.tree.y_current.search_y_max()
            self._step_p2(y_max)
            self._step_r()
            rn = norm(self._vector_r)
            if rn >= self.tree.riter[self.tree.current_level + 1]:
                self.tree.step_z(y=y_max, i_max=i_max, d=self.parameter_d, u=self._vector_u)
                if self.tree.current_level == self.tree.kc - 2:
                    self.tree.current_level += 1
                    self.tree.set_meta(self.tree.y_current)
                    self.tree.set_meta(y_max)
                else:
                    if self.tree.is_empty():
                        self.tree.set_meta(self.tree.y_current)
                        if self.mode != 2:
                            self._create_neurons(vector_type, avclass)
                    else:
                        if self.tree.current_level <= self.tree.kc - 2:
                            self.tree.to_next_level(y_max)
            else:
                y_max.flag_freeze = True

        if self.tree.is_all_freeze():
            self.tree.set_meta(self.tree.y_current)
            self.tree.unfreeze()
            if self.mode != 2:
                self._create_neurons(vector_type, avclass)
        self.tree.to_first_level()
        recognition_type = self.tree.current_vector_type
        recognition_avclass = self.tree.current_vector_avclass
        self.tree.clear_tree()
        return recognition_type, recognition_avclass

    def load_tree(self, filename: str) -> Tree:
        try:
            file_tree_parameters = open(filename, 'r')
            parameters = load(file_tree_parameters)
            file_tree_parameters.close()
            self.tree = Tree(RiterF=parameters['RiterF'], riter=parameters['riter'], kc=parameters['kc'],
                             n=parameters['n'])

            self.tree.load_memory_tree(filename)
            return self.tree
        except FileNotFoundError as e:
            write_logs(str(e))
            return Tree()
