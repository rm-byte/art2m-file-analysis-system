from json import dump, dumps, loads
from datetime import datetime

from neuron import Y


class Tree:
    def __init__(self, RiterF=None, riter=None, kc=None, n=None):
        if RiterF:
            self.RiterF = RiterF
        else:
            self.RiterF = 0.9999
        if riter:
            self.riter = riter
        else:
            self.riter = self.get_riter()
        if kc:
            self.kc = kc
        else:
            self.kc = len(self.riter)
        self.root = None
        self.y_current = None
        self.current_level = 0
        if n:
            self.n = n
        else:
            self.n = None
        self.neurons_num_per_level = [0] * self.kc
        self.current_vector_type = None
        self.current_winner = None
        self.current_vector_avclass = None

    def set_n(self, n: int) -> None:
        self.n = n

    def get_riter(self) -> list:
        tmp = 0.8
        riter = [tmp]
        while tmp < self.RiterF:
            tmp = tmp + 0.7 * (1 - tmp)
            riter.append(tmp)
        print('Riter:', riter)
        return riter

    def is_all_freeze(self) -> bool or None:
        if self.y_current.y_next:
            for y in self.y_current.y_next:
                if not y.flag_freeze:
                    return False
            return True
        else:
            return None

    def step_z(self, y: Y, d: float, u: list, i_max: int) -> None:
        if i_max > -1:
            for i in range(self.n):
                y.z_weight[i] += d * (u[i] - y.z_weight[i] * (1 - d))

        else:
            for i in range(self.n):
                y.z_weight[i] = d * u[i]

    def step_y(self, p: list) -> None:
        if self.y_current.y_next:
            for y in self.y_current.y_next:
                if not y.flag_freeze:
                    y.y_value = 0
                    for i, j in zip(y.z_weight, p):
                        y.y_value += i * j
        else:
            self.y_current.y_value = 0
            for i, j in zip(self.y_current.z_weight, p):
                self.y_current.y_value += i * j

    def create_root(self) -> None:
        self.root = Y(self.n)
        self.y_current = self.root
        self.neurons_num_per_level[self.current_level] += 1
        self.y_current.set_indexes(layer=self.current_level, number=self.neurons_num_per_level[self.current_level])

    def create_neuron(self, vector_type: int, avclass: str) -> None:
        y = Y(self.n)
        y.y_previous = self.y_current
        self.y_current.y_next.append(y)
        self.y_current = y

        self.current_level += 1
        self.neurons_num_per_level[self.current_level] += 1

        self.y_current.set_indexes(layer=self.current_level, number=self.neurons_num_per_level[self.current_level])
        self.y_current.type = vector_type
        self.y_current.avclass = avclass

    def unfreeze(self) -> None:
        if self.y_current.y_next:
            for y in self.y_current.y_next:
                y.flag_freeze = False

    def is_empty(self) -> bool:
        return False if self.y_current.y_next else True

    def to_first_level(self) -> None:
        self.y_current = self.root
        self.current_level = 0

    def to_next_level(self, y: Y) -> None:
        self.unfreeze()
        self.y_current = y
        self.current_level += 1
        self.unfreeze()

    def is_last_level(self) -> bool:
        return False if self.current_level < self.kc - 1 else True

    def set_meta(self, y: Y) -> None:
        if y.index_layer == self.kc - 1:
            self.current_vector_type = y.type
            self.current_vector_avclass = y.avclass
            self.current_winner = y

    def _is_all_neurons_scanned(self) -> bool:
        for i in self.y_current.y_next:
            if i.scanned is False:
                return False
        return True

    def _neuron_to_json(self) -> str:
        neuron = {'index_layer': self.y_current.index_layer,
                  'index_number': self.y_current.index_number,
                  'z_weight': self.y_current.z_weight,
                  'y_value': self.y_current.y_value}

        return dumps(neuron)

    def _set_scanned(self) -> None:
        self.y_current.scanned = True

    def _set_current(self, y: Y) -> None:
        self.y_current = y

    def _get_unscanned(self) -> Y or None:
        for y in self.y_current.y_next:
            if y.scanned is False:
                return y
        return None

    def _is_root(self) -> bool:
        return True if self.y_current.index_layer == 0 else False

    def _load_neuron(self, neuron: dict) -> None:
        y = Y(self.n)
        if neuron['index_layer'] == 0:
            self.root = y
            self.y_current = self.root
        else:
            y.y_previous = self.y_current
            self.y_current.y_next.append(y)
            self.y_current = y
        self.neurons_num_per_level[self.current_level] += 1
        if neuron['index_layer'] != self.kc - 1:
            self.current_level += 1
        self.y_current.set_indexes(layer=neuron['index_layer'], number=neuron['index_number'])
        self.y_current.z_weight = neuron['z_weight']
        self.y_current.y_value = neuron['y_value']

    def _to_previous_level(self) -> None:
        self.y_current = self.y_current.y_previous
        self.current_level = self.y_current.index_layer + 1

    def load_memory_tree(self, filename: str) -> None:
        date = filename.split('_')[2]
        file = open('tree/memory_tree_' + date + '.txt', 'r')
        self.set_n(self.n)
        last_level_reached = False
        for line in file:
            neuron = loads(line)
            if last_level_reached:
                last_level_reached = False
                while self.y_current.index_layer >= neuron['index_layer']:
                    self._to_previous_level()
            self._load_neuron(neuron)
            if neuron['index_layer'] == self.kc - 1:
                last_level_reached = True
        self.to_first_level()
        file.close()

    def unload_tree(self) -> None:
        file_tree_parameters = open('tree/tree_parameters_' + str(datetime.now().date()) + '.txt', 'w')
        parameters = {'RiterF': self.RiterF, 'kc': self.kc, 'riter': self.riter, 'n': self.n}
        dump(parameters, file_tree_parameters)
        file_tree_parameters.close()

        file_tree = open('tree/memory_tree_' + str(datetime.now().date()) + '.txt', 'w')
        self.to_first_level()
        file_tree.write(self._neuron_to_json() + '\n')
        self._set_scanned()

        while self.y_current.index_layer <= self.kc - 1:
            if self._is_all_neurons_scanned():
                if self._is_root():
                    break
                else:
                    self._set_current(self.y_current.y_previous)
            else:
                y = self._get_unscanned()
                self._set_current(y)
                file_tree.write(self._neuron_to_json() + '\n')
                self._set_scanned()
            if self.y_current.index_layer == self.kc - 1:
                self._set_current(self.y_current.y_previous)
        file_tree.close()
        self.clear_tree()

    def _neuron_to_node(self, y: Y) -> str:
        full = str(y.index_layer) + ',' + str(y.index_number)
        if y.index_layer != self.kc - 1:
            full += ' '
        else:
            full += '|' + str(y.type)
            if y.avclass:
                full += '|' + str(y.avclass) + '|\n'
            else:
                full += '|\n'
        return full

    def unload_tree_graph(self) -> None:
        file = open('result/graph_' + str(datetime.now().date()) + '.txt', 'w')
        self.to_first_level()
        file.write(self._neuron_to_node(self.y_current))
        self._set_scanned()

        while self.y_current.index_layer <= self.kc - 1:
            if self._is_all_neurons_scanned():
                if self._is_root():
                    break
                else:
                    self._set_current(self.y_current.y_previous)
            else:
                y = self._get_unscanned()
                self._set_current(y)
                file.write(self._neuron_to_node(self.y_current.y_previous))
                file.write(self._neuron_to_node(self.y_current))
                self._set_scanned()
            if self.y_current.index_layer == self.kc - 1:
                self._set_current(self.y_current.y_previous)
        file.close()
        self.clear_tree()

    def _get_scanned(self) -> Y or None:
        for y in self.y_current.y_next:
            if y.scanned is True:
                return y
        return None

    def _is_all_neurons_unscanned(self) -> bool:
        for i in self.y_current.y_next:
            if i.scanned is True:
                return False
        return True

    def clear_tree(self):
        self.to_first_level()
        self.y_current.scanned = False
        self.y_current.flag_freeze = False

        while self.y_current.index_layer <= self.kc - 1:
            if self._is_all_neurons_unscanned():
                if self._is_root():
                    break
                else:
                    self._set_current(self.y_current.y_previous)
            else:
                y = self._get_scanned()
                self._set_current(y)
                self.y_current.scanned = False
                self.y_current.flag_freeze = False
            if self.y_current.index_layer == self.kc - 1:
                self._set_current(self.y_current.y_previous)
